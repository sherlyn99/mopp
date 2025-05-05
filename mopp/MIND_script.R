required_packages <- c(
  "stringr", "ggplot2", "FactoMineR", "factoextra",
  "reshape", "reshape2", "gplots", "edgeR",
  "dplyr", "svglite", "RColorBrewer", "data.table"
)

# Function to check and install packages
for (pkg in required_packages) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      message(paste("Installing package:", pkg))
      install.packages(pkg, dependencies = TRUE)
      
    } 
}

library(stringr)
library(ggplot2)
library(FactoMineR)
library(factoextra)
library(reshape)
library(reshape2)
library(gplots)
library(edgeR)
library(dplyr)
library(svglite)
library(RColorBrewer)
library(data.table)

args <- commandArgs(trailingOnly = TRUE)
input <- args[1]
output <- args[2]
UnirefWithCoords <- args[3]
KeggMapping <- args[4]

setwd(output)
# Read the input data
data <- fread(input, 
              sep = "\t", 
              header = TRUE, 
              na.strings = "", 
              check.names = FALSE)
# Split column into genus_strain and Uniref
data[, c("genus_strain", "Uniref") := tstrsplit(`#FeatureID`, "\\|", keep = c(1,2))]

# Load gene length information
uniref_coords <- fread(UnirefWithCoords, sep = "\t", header = TRUE)
uniref_coords[, gene_len := abs(End - Start)]

# Merge with main data
data <- merge(data, uniref_coords, by = "Uniref")

# Define RPKM function
rpkm_fun <- function(x, gene_len) {
  x / ((1 / gene_len) * (sum(x) / 1e6)) 
}

# Identify omics columns
omic_cols <- names(data)[str_detect(names(data), "metaG|metaT|metaRS")]

# Apply RPKM normalization
data[, (omic_cols) := lapply(.SD, rpkm_fun, gene_len), .SDcols = omic_cols]

# KEGG annotation
kegg <- fread(KeggMapping, 
              col.names = c("ko", "kegg", "Uniref", "pathway"),
              na.strings = "")

merged_data <- merge(data, kegg, by = "Uniref")

kegg_annot_noNA <- merged_data[!is.na(pathway)]


# Aggregate by gene or pathway
meta_cols <- grep("metaG|metaT|metaRS", names(kegg_annot_noNA), value = TRUE)

# Aggregate by pathway and genus_strain
agg_pathway <- kegg_annot_noNA[, lapply(.SD, sum), 
                               by = .(pathway, genus_strain), 
                               .SDcols = meta_cols]

# Aggregate by gene name and genus_strain (excluding hypothetical proteins)
agg_protein <- kegg_annot_noNA[Name != "hypothetical protein", 
                               lapply(.SD, sum), 
                               by = .(Name, genus_strain), 
                               .SDcols = meta_cols]

# TE Calculations

process_omic_matrix <- function(df, pattern) {
  mat <- as.matrix(df[, str_detect(names(df), pattern), with = FALSE])
  colnames(mat) <- str_replace(colnames(mat), paste0("_", pattern), "")
  mat[mat < 10] <- 0  # Filter low counts
  return(mat)
}

metaG_mat <- process_omic_matrix(agg_pathway, "metaG")
metaT_mat <- process_omic_matrix(agg_pathway, "metaT")
metaRS_mat <- process_omic_matrix(agg_pathway, "metaRS")

# Calculate TE matrix
TE_mat <- metaRS_mat / metaT_mat
colnames(TE_mat) <- paste0(colnames(TE_mat), "_TE")

# Handle special cases
TE_mat[is.na(TE_mat) | is.infinite(TE_mat)] <- 0
TE_mat[TE_mat < 1] <- 0

TE_bypathway <- cbind(agg_pathway[, .(pathway, genus_strain)], TE_mat)
TE_byprotein <- cbind(agg_protein[, .(Name, genus_strain)], TE_mat)


# TE Based functional profiling
TE_pca <- TE_bypathway[, grep("_TE$", names(TE_bypathway), value = TRUE), with = FALSE] #Clustering based on TE column only. Basically replace with only TE columns from syncom

TE_pca <- if(ncol(TE_pca) > 1) {
  apply(TE_pca, 1, mean, na.rm = TRUE)  # Multi-column averaging
} else {
  TE_pca[, 1]  # Single column case
}

TE_pca <- data.frame(cbind(TE_bypathway[, c("pathway", "genus_strain")], TE = TE_pca))

TE_pca <- reshape(TE_pca,
                  direction = "wide", 
                  idvar = "genus_strain", 
                  timevar = "pathway")

TE_pca[is.na(TE_pca)] <- 0

rownames(TE_pca) <- TE_pca$genus_strain
TE_pca <- TE_pca[, !colnames(TE_pca) == "genus_strain"]

TE_pca <- TE_pca[apply(TE_pca, 1, sum)!=0, ]
TE_pca <- TE_pca[, apply(TE_pca, 2, sum)!=0]

colnames(TE_pca) <- gsub("TE.", "", colnames(TE_pca))
colnames(TE_pca) <- str_split(colnames(TE_pca), "\\[", simplify = TRUE)[,1]

TE_pca_adjusted <- TE_pca

# Add 0.001 to values between 0-1 (add 1 to all others)
TE_pca_adjusted[TE_pca_adjusted > 0 & TE_pca_adjusted < 1] <- TE_pca_adjusted[TE_pca_adjusted > 0 & TE_pca_adjusted < 1] + 0.001
TE_pca_adjusted <- TE_pca_adjusted + 1

# Then perform PCA
pca <- PCA(log(TE_pca_adjusted),
           scale.unit = FALSE,
           graph = FALSE,
           ncp = 5)

var_explained <- data.frame(pca$eig)
var_explained$PC <- rownames(var_explained)
var_explained$PC <- ordered(var_explained$PC, levels = unique(var_explained$PC))

optimal_pc <- var_explained %>%
  filter(cumulative.percentage.of.variance > 80) %>%
  slice(1) %>%  # Take the first row that meets the condition
  pull(PC)

# Redefine the PCA plot with the optimal number of principal components
pca <- PCA(log(TE_pca_adjusted),
           scale.unit = FALSE,
           graph = FALSE,
           ncp = as.numeric(optimal_pc))

var_explained <- data.frame(pca$eig)
var_explained$PC <- rownames(var_explained)
var_explained$PC <- ordered(var_explained$PC, levels = unique(var_explained$PC))

# Cluster analysis

TE_clust <- HCPC(pca, 
                 nb.clust = -1, 
                 metric = "euclidean", 
                 method = "ward",
                 graph = FALSE
)
image <- fviz_cluster(TE_clust, repel = TRUE, labelsize = 13, 
                      ggtheme = theme(panel.background = element_rect(fill = "white"), panel.grid.major = element_line(colour = "gray92"), panel.grid.minor = element_line(colour = "gray92")) 
) 

# Output #1. Cluster plot of species by pathway.
ggsave(file="GuildClusterplot.svg", plot=image, height = 4.5, width = 6.5, dpi = 600)

#  Guids TE tree analysis.
distmat <- as.data.frame(as.matrix(dist(pca$ind$coord, method = "euclidean")))
distmat <- distmat[rev(c(colnames(distmat))), rev(c(colnames(distmat)))]
distmat[distmat == 0] <- NA

tree <- hclust(dist(pca$ind$coord, method = "euclidean"), method = "ward.D2")
cutree(tree, k = 6)

# Output #2. TE Tree.
svg(paste0("GuildTree", as.numeric(optimal_pc), "PCs.svg"), height = 5, width = 6)
plot(x = tree, labels =  row.names(tree), cex = 1, hang = -1)
dev.off()

# Calclulate competition score
score <- data.frame(t(apply(distmat, 1, function(x) - (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE))))

apply(score, 1, function(x)sum(x, na.rm = TRUE))
apply(score, 1, function(x)summary(x, na.rm = TRUE))

cool = rainbow(50, start=rgb2hsv(col2rgb('cyan'))[1], end=rgb2hsv(col2rgb('blue'))[1])
warm = rainbow(50, start=rgb2hsv(col2rgb('red'))[1], end=rgb2hsv(col2rgb('yellow'))[1])
cols = c(rev(cool), "lightcyan", rev(warm))
cols = c(rev(cool), "lemonchiffon", rev(warm))
cols = c(rev(cool),  rgb(124, 248, 248, maxColorValue=255, alpha=255),  rev(warm))

mypalette <- colorRampPalette(cols)(101)

#Output #3. Competition Matrix.
svg(paste0("CompetitionMatrix_",as.numeric(optimal_pc), "PCs.svg"))
heatmap.2(as.matrix(score), 
          trace = "none", 
          Rowv = FALSE,
          Colv = FALSE, 
          margins = c(10,10), 
          col = mypalette, 
          labCol=as.expression(lapply(colnames(score), function(a) bquote(italic(.(a))))),
          labRow=as.expression(lapply(rownames(score), function(a) bquote(italic(.(a))))),
          scale = "none", 
          #side = -1, 
          na.color = "gray90",
          sepwidth=c(0.01,0.01),
          rowsep=c(0:16), 
          colsep=c(0,14), 
          sepcolor = "white"
)
dev.off()

# Binary (competition yes/no)

score[score>0] <- 1
# score[score==0] <- 0.5            YES OR NOT 
score[score<0] <- 0


#Output #4. Binary Competition Matrix.
svg(paste0("BinaryCompetitionMatrix_",as.numeric(optimal_pc), "PCs.svg"))
heatmap.2(as.matrix(score), 
          trace = "none", 
          Rowv = FALSE,
          Colv = FALSE, 
          margins = c(10,10), 
          col=bluered, 
          scale = "none", 
          na.color = "black"
          
          
)
dev.off()

# MiND algorithm

TE_import <- TE_byprotein %>%
  filter(str_detect(Name, "take|import")) %>%
  select(matches("_TE$")) %>%
  as.data.frame()  # Ensures data frame output
TE_import <- apply(TE_import, 1, mean)
TE_import <- data.frame(cbind(TE_byprotein[str_detect(TE_byprotein$Name, "take")|str_detect(TE_byprotein$Name, "import"), c("Name", "genus_strain")], TE_import))  #test


TE_import <- reshape(TE_import,
                     direction = "wide", 
                     idvar = "genus_strain", 
                     timevar = "Name")


TE_import[is.na(TE_import)] <- 0

rownames(TE_import) <- TE_import$genus_strain
TE_import <- TE_import[, !colnames(TE_import) == "genus_strain"]

colnames(TE_import) <- str_replace(colnames(TE_import), "TE_import.", "")

TE_import <- TE_import[, colnames(TE_import)%in%colnames(TE_import)]

ncol( TE_import[, apply(TE_import, 2, sum)!=0])

# Same order than guild clustering
TE_import$Tax <- rownames(TE_import)
TE_import$Tax <- ordered(TE_import$Tax, levels = colnames(TE_import))

TE_import <- TE_import[order(TE_import$Tax), ]
TE_import <- TE_import[, colnames(TE_import)!="Tax"]

TE_import <- data.frame(t(TE_import))
TE_import$gene <- rownames(TE_import)
TE_import <- TE_import[sort(TE_import$gene), ]
TE_import <- TE_import[, colnames(TE_import) != "gene"]


# Niche Determination


# Set up clustering and distances functions

hclustfunc <- function(x) hclust(x, method="ward.D2") # clustering ward
distfunc <- function(x) dist(x, method="euclidean")   # euclidean distances 

# Create custom color palette

cool = rainbow(50, start=rgb2hsv(col2rgb('cyan'))[1], end=rgb2hsv(col2rgb('blue'))[1])
warm = rainbow(50, start=rgb2hsv(col2rgb('red'))[1], end=rgb2hsv(col2rgb('yellow'))[1])
cols = c(rev(cool),  rev(warm))

mypalette <- colorRampPalette(c("lightyellow1", rev(warm)))(21)

TE_import <- TE_import[apply(TE_import, 1, sum)!=0, ]

#Output #5 Niche determination
svg("TE_import_heatmap.svg", height = 10, width = 10)
heatmap.2(as.matrix(log(TE_import + 0.0001)),
          trace = "none",
          hclustfun = hclustfunc,
          distfun = distfunc,
          col = mypalette,
          scale = "none",
          # Rowv = FALSE,
          # Colv = FALSE,
          margins=c(15,28),
          lhei=c(1,6), lwid=c(1,5)
)
dev.off()

# Niche Determination by MetaT

metaT_import <- agg_protein %>%
  filter(str_detect(Name, "take|import")) %>%
  select(matches("metaT")) %>%
  as.data.frame()

metaT_import <- apply(metaT_import, 1, function(x)mean(x, na.rm = TRUE))

metaT_import <- data.frame(cbind(agg_protein[str_detect(agg_protein$Name, "take")|str_detect(agg_protein$Name, "import"), c("Name", "genus_strain")], metaT_import))

metaT_import <- reshape(metaT_import,
                        direction = "wide", 
                        idvar = "genus_strain", 
                        timevar = "Name")

metaT_import[is.na(metaT_import)] <- 0

rownames(metaT_import) <- metaT_import$genus_strain
metaT_import <- metaT_import[, !colnames(metaT_import) == "genus_strain"]

colnames(metaT_import) <- str_replace(colnames(metaT_import), "metaT_import.", "")

# Same order than guild clustering
metaT_import$Tax <- rownames(metaT_import)
metaT_import$Tax <- ordered(metaT_import$Tax , levels = rev(c(metaT_import)))

metaT_import <- metaT_import[order(metaT_import$Tax), ]
metaT_import <- metaT_import[, colnames(metaT_import)!="Tax"]

metaT_import <- data.frame(t(metaT_import))
metaT_import$gene <- rownames(metaT_import)
metaT_import <- metaT_import[sort(metaT_import$gene), ]
metaT_import <- metaT_import[, colnames(metaT_import) != "gene"]


#Output #6
svg("metaT_import_heatmap.svg", height = 15, width = 10)
heatmap.2(as.matrix(metaT_import),
          trace = "none",
          hclustfun = hclustfunc,
          distfun = distfunc,
          col = bluered,
          scale = "row",
          Rowv = FALSE,
          Colv = FALSE,
          margins=c(10,25),
          lhei=c(1,8), lwid=c(1,5),
          labCol=as.expression(lapply(colnames(metaT_import), function(a) bquote(italic(.(a)))))
)
dev.off()


