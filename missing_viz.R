library(tidyverse)
library(patchwork)
library(Lock5withR)

missing_vis <- function(df, percent = TRUE) {
  counts <- colSums(is.na(df)) %>%
    sort(decreasing = TRUE)
  counts <- data.frame(counts)
  names(counts)[1] = 'count'
  counts$id <- rownames(counts)
  counts$perc <- counts$count / nrow(df)
  
  missing_patterns <- data.frame(is.na(df)) %>%
    group_by_all() %>%
    count(name = "count", sort = TRUE) %>%
    ungroup()
  
  pattern_counts <- missing_patterns %>%
    select(count)
  pattern_counts$id <- rownames(pattern_counts)
  pattern_counts$perc <- pattern_counts$count / nrow(df)
  
  missing_patterns <- missing_patterns %>%
    select(!count)
  
  y <- factor(colnames(missing_patterns), levels = reorder(counts$id, - counts$count))
  x <- as.numeric(rownames(missing_patterns))
  df2 <- expand.grid(x = x, y = y)
  
  z <- c()
  for (row in 1:nrow(df2)) {
    y <- df2[row, 'y']
    x <- df2[row, 'x']
    val <- missing_patterns[x, y]
    z <- append(z, val)
  }
  df2$z <- z
  df2 <- mutate(df2, val = if_else(z == TRUE, 1, 0))
  df2$x2 <- abs(df2$x - (max(df2$x) + 1))
  
  complete_rownum <- as.numeric(df2 %>%
                                  group_by(x) %>%
                                  summarise(sum_val = sum(val)) %>%
                                  filter(sum_val == 0) %>%
                                  select(x))
  
  df2 <- within(df2, val[x == complete_rownum] <- 2)
  pattern_counts$fill1 = 0
  pattern_counts <- within(pattern_counts, fill1[id == complete_rownum] <- 1)
  
  tile_width <- 0.95
  tile_height <- 0.95
  
  heat <- ggplot(df2) +
    geom_tile(aes(x=x2, y=y, fill = val,
                  width = tile_width,
                  height = tile_height)) +
    scale_x_discrete('Pattern', limits = factor(max(df2$x2):min(df2$x2))) +
    scale_y_discrete(guide = guide_axis(n.dodge = 3)) +
    theme(legend.position = 'none') +
    ylab("Variable") +
    annotate("text",
             x = abs(complete_rownum - (max(df2$x) + 1)),
             y = 3,
             label = "Complete Cases") +
    coord_flip()
  
  col_param = 'perc'
  if (percent == FALSE) {
    col_param = 'count'
  }
  
  top_plot <- ggplot(counts, aes(x = reorder(id, -.data[[col_param]]),
                                 y = .data[[col_param]])) +
    geom_col() +
    theme(axis.text.x = element_blank()) +
    xlab('') +
    ylab(paste0(col_param, " missing")) +
    ggtitle("Missing Data Report")
  
  side_plot <- ggplot(data=pattern_counts) +
    geom_col(mapping=aes(x=id, y=.data[[col_param]], fill=fill1)) +
    scale_x_discrete(name="", limits = factor(nrow(pattern_counts):1)) +
    theme(axis.text.y = element_blank(),
          legend.position = 'none') +
    ylab(paste0(col_param)) +
    coord_flip()
  
  
  layout <- "
  AAAAA##
  BBBBBCC
  BBBBBCC
  BBBBBCC
  "
  (top_plot + heat + side_plot) +
    plot_layout(design = layout)
}

