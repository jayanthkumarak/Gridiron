# Gridiron R Analytics Service - Startup Script
# Pre-loads nflfastR data before starting Plumber

library(nflfastR)
library(nflreadr)
library(plumber)
library(jsonlite)
library(dplyr)

cat("========================================\n")
cat("Gridiron R Analytics Service\n")
cat("========================================\n\n")

# Load current season play-by-play data
cat("Loading 2024-2025 season data...\n")
start_time <- Sys.time()

# Load play-by-play data (will be available globally)
tryCatch({
  # Load current and previous season for comparison queries
  pbp_data <<- nflreadr::load_pbp(2024:2025)
  
  # Store in global environment for plumber to access
  assign("pbp_data", pbp_data, envir = .GlobalEnv)
  
  end_time <- Sys.time()
  load_duration <- round(as.numeric(difftime(end_time, start_time, units = "secs")), 2)
  
  cat(sprintf("✓ Loaded %s plays in %s seconds\n", 
              format(nrow(pbp_data), big.mark = ","), 
              load_duration))
  cat(sprintf("✓ Seasons: %s\n", paste(unique(pbp_data$season), collapse = ", ")))
  
}, error = function(e) {
  cat(sprintf("✗ Error loading data: %s\n", e$message))
  cat("Attempting to load 2024 only...\n")
  
  pbp_data <<- nflreadr::load_pbp(2024)
  assign("pbp_data", pbp_data, envir = .GlobalEnv)
  
  cat(sprintf("✓ Loaded %s plays from 2024 season\n", 
              format(nrow(pbp_data), big.mark = ",")))
})

cat("\nStarting Plumber API on port 8787...\n")
cat("========================================\n\n")

# Start Plumber API
pr <- plumber::plumb("plumber.R")
pr$run(host = "0.0.0.0", port = 8787)
