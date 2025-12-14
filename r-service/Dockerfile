# Gridiron R Analytics Service
# Base: rocker/tidyverse with R 4.3

FROM rocker/tidyverse:4.3

# Install system dependencies for nflfastR
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
RUN R -e "install.packages(c('plumber', 'jsonlite', 'glue'), repos='https://cloud.r-project.org/')"

# Install nflfastR and nflreadr (optimized data loading)
RUN R -e "install.packages(c('nflfastR', 'nflreadr'), repos='https://cloud.r-project.org/')"

# Create working directory
WORKDIR /app

# Copy R scripts
COPY plumber.R .
COPY startup.R .

# Expose port
EXPOSE 8787

# Pre-load data and start Plumber
CMD ["Rscript", "startup.R"]
