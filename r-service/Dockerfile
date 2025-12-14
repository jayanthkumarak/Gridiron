# Gridiron R Analytics Service
FROM --platform=linux/amd64 rocker/tidyverse:4.3

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libsodium-dev \
    && rm -rf /var/lib/apt/lists/*

# Install ALL R packages in one command to ensure they're all present
RUN R -e "install.packages(c('plumber', 'jsonlite', 'glue', 'nflfastR', 'nflreadr'), repos='https://cloud.r-project.org/', dependencies=TRUE)"

# Verify plumber installed
RUN R -e "library(plumber); cat('plumber OK\n')"

WORKDIR /app
COPY plumber.R .
COPY startup.R .

EXPOSE 8787
CMD ["Rscript", "startup.R"]
