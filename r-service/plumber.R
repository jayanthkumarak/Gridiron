# Gridiron R Analytics Service - Plumber API
# Exposes endpoints for R script execution

library(plumber)
library(jsonlite)
library(dplyr)

#* @apiTitle Gridiron R Analytics API
#* @apiDescription Execute R scripts for NFL analytics using nflfastR

#* Health check endpoint
#* @get /health
function() {
  tryCatch({
    plays <- nrow(pbp_data)
    seasons <- unique(pbp_data$season)
    
    list(
      status = "ok",
      data_loaded = TRUE,
      total_plays = plays,
      seasons = seasons,
      timestamp = Sys.time()
    )
  }, error = function(e) {
    list(
      status = "error",
      data_loaded = FALSE,
      error = e$message
    )
  })
}

#* Execute R script and return JSON
#* @post /execute
#* @param script:str R script to execute
function(script) {
  # Validate input
  if (missing(script) || is.null(script) || script == "") {
    return(list(
      success = FALSE,
      error = "No script provided"
    ))
  }
  
  # Security: Basic script validation
  # Block dangerous operations
  forbidden_patterns <- c(
    "system\\s*\\(",
    "file\\.",
    "write\\.",
    "unlink\\s*\\(",
    "Sys\\.setenv",
    "rm\\s*\\(",
    "library\\s*\\(",
    "require\\s*\\(",
    "install\\.packages",
    "source\\s*\\("
  )
  
  for (pattern in forbidden_patterns) {
    if (grepl(pattern, script, ignore.case = TRUE)) {
      return(list(
        success = FALSE,
        error = paste("Forbidden pattern detected:", pattern)
      ))
    }
  }
  
  # Execute script in controlled environment
  tryCatch({
    # Create execution environment with access to data
    exec_env <- new.env()
    exec_env$pbp_data <- pbp_data
    exec_env$filter <- dplyr::filter
    exec_env$select <- dplyr::select
    exec_env$mutate <- dplyr::mutate
    exec_env$summarize <- dplyr::summarize
    exec_env$summarise <- dplyr::summarise
    exec_env$group_by <- dplyr::group_by
    exec_env$ungroup <- dplyr::ungroup
    exec_env$arrange <- dplyr::arrange
    exec_env$desc <- dplyr::desc
    exec_env$n <- dplyr::n
    exec_env$mean <- base::mean
    exec_env$sum <- base::sum
    exec_env$round <- base::round
    exec_env$head <- utils::head
    exec_env$tail <- utils::tail
    exec_env$unique <- base::unique
    exec_env$length <- base::length
    exec_env$is.na <- base::is.na
    exec_env$na.rm <- TRUE
    
    # Parse and evaluate script
    parsed <- parse(text = script)
    result <- eval(parsed, envir = exec_env)
    
    # Convert result to JSON-serializable format
    if (is.data.frame(result)) {
      result <- as.list(result)
    }
    
    list(
      success = TRUE,
      result = result
    )
    
  }, error = function(e) {
    list(
      success = FALSE,
      error = e$message
    )
  })
}

#* Get available teams
#* @get /teams
function() {
  tryCatch({
    teams <- sort(unique(c(pbp_data$home_team, pbp_data$away_team)))
    teams <- teams[!is.na(teams) & teams != ""]
    
    list(
      success = TRUE,
      teams = teams
    )
  }, error = function(e) {
    list(
      success = FALSE,
      error = e$message
    )
  })
}

#* Get data schema (column names and types)
#* @get /schema
function() {
  tryCatch({
    # Key columns for analytics
    key_columns <- c(
      "play_id", "game_id", "posteam", "defteam", "down", "ydstogo",
      "yardline_100", "qtr", "play_type", "yards_gained", "epa", "wp",
      "wpa", "cpoe", "air_yards", "success", "pass", "rush"
    )
    
    available <- key_columns[key_columns %in% names(pbp_data)]
    
    schema <- lapply(available, function(col) {
      list(
        name = col,
        type = class(pbp_data[[col]])[1],
        sample = head(unique(pbp_data[[col]]), 5)
      )
    })
    
    list(
      success = TRUE,
      total_columns = ncol(pbp_data),
      key_columns = schema
    )
  }, error = function(e) {
    list(
      success = FALSE,
      error = e$message
    )
  })
}
