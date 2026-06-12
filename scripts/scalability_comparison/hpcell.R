library(HPCell)
library(crew)
library(Seurat)
library(scuttle)
library(methods)

# Input dataset
input_hpc <- c(
  HLCAv1 = "data/pipeline/load_data/download/HLCAv1_core.h5ad"
)

input_hpc |>
  initialise_hpc(
    gene_nomenclature = "symbol",
    data_container_type = "anndata",
    store = "data/pipeline/scalability",
    computing_resources = crew_controller_local(workers = 4)
  ) |>

  # 1) Normalize counts
  hpc_iterate(
    target_output = "normalized_data",
    user_function = (function(x, target_sum = 10000) {
      if (is(x, "Seurat")) {
        NormalizeData(
          object = x,
          normalization.method = "LogNormalize",
          scale.factor = target_sum
        )
      } else if (is(x, "SingleCellExperiment")) {
        logNormCounts(x)
      } else {
        stop("Unsupported object class")
      }
    }) |> quote(),
    x = "data_object" |> is_target(),
    target_sum = 10000,
    packages = c("Seurat", "SingleCellExperiment", "scuttle", "methods")
  ) |>

  # 2) Find highly variable genes (non-batch-aware)
  hpc_iterate(
    target_output = "hvg_data",
    user_function = (function(x, n_top_genes = 2000) {
      if (is(x, "Seurat")) {
        FindVariableFeatures(
          object = x,
          selection.method = "vst",
          nfeatures = n_top_genes
        )
      } else {
        stop("HVG selection is implemented here for Seurat objects only")
      }
    }) |> quote(),
    x = "normalized_data" |> is_target(),
    n_top_genes = 2000,
    packages = c("Seurat", "methods")
  ) |>

  # 3) Run PCA
  hpc_iterate(
    target_output = "pca_data",
    user_function = (function(x) {
      RunPCA(object = x)
    }) |> quote(),
    x = "hvg_data" |> is_target(),
    packages = "Seurat"
  ) |>

  # 4) Build nearest-neighbor graph
  hpc_iterate(
    target_output = "neighbors_data",
    user_function = (function(x) {
      FindNeighbors(object = x)
    }) |> quote(),
    x = "pca_data" |> is_target(),
    packages = "Seurat"
  ) |>

  # 5) Run UMAP
  hpc_iterate(
    target_output = "umap_data",
    user_function = (function(x) {
      RunUMAP(object = x, dims = 1:30)
    }) |> quote(),
    x = "neighbors_data" |> is_target(),
    packages = "Seurat"
  )