library(tidyverse)
library(patchwork)
plot_missing <- function(x, percent = TRUE) {	
  na_count_all <- data.frame(is.na(x)) %>%	
    group_by_all() %>%	
    count(name = "count", sort = TRUE) %>%	
    ungroup() %>%	
    rownames_to_column("pattern")	
  
  na_count_all <- na_count_all %>% 
    mutate(pattern = factor(pattern, levels = nrow(na_count_all):1))
  
  # count the number of columns with missing values; will be used later to determine if there's a "none missing" pattern	
  na_count_all <- na_count_all %>% 	
    rowwise() %>%	
    mutate(num_missing_cols = sum(c_across(where(is.logical))))	
  
  # data frame for missing patterns bar chart	
  na_count_by_pattern <- na_count_all %>% 	
    select(pattern, count, num_missing_cols) %>% 	
    mutate(none_missing = ifelse(num_missing_cols == 0, TRUE, FALSE))
  
  # data frame for missing by column bar chart	
  na_count_by_column <- data.frame(is.na(x)) %>%	
    colSums() %>% 	
    sort(decreasing = TRUE) %>% 	
    enframe(name = "var", value = "count")	
  
  # tidy and sort na_count_all by column counts	
  na_count_all_tidy <- na_count_all %>% 	
    pivot_longer(where(is.logical), names_to = "variable") %>%	
    mutate(variable = factor(variable, levels = na_count_by_column$var))  %>% 	
    mutate(none_missing = ifelse(num_missing_cols == 0, TRUE, FALSE))	
  
  # main plot
  main_plot <- ggplot(na_count_all_tidy, aes(variable, pattern, fill = factor(value), alpha = none_missing)) +	
    geom_tile(color = "white") +	
    scale_fill_manual(values = c("grey70", "mediumpurple")) +	
    scale_alpha_manual(values = c(.7, 1)) +	
    ylab("missing pattern") +	
    guides(fill = "none", alpha = "none") +	
    theme_classic(12)	
  
  # check for "none missing" pattern
  none_missing_pattern <- na_count_by_pattern %>%
    filter(none_missing) %>% pull(pattern)
  
  if (length(none_missing_pattern) > 0) {	
    main_plot <- main_plot +	
      annotate("text", x = (ncol(na_count_all)-2)/2,	
               y = nrow(na_count_all) + 1 - as.numeric(as.character(none_missing_pattern)),	
               label = "complete cases")	
  }	
  
  # margin plots
  
  denom <- ifelse(percent, nrow(x)/100, 1)
  
  missing_by_column_plot <- ggplot(na_count_by_column, aes(fct_inorder(var), count/denom)) +	
    geom_col(fill = "cornflowerblue", alpha = .7) + xlab("") +	
    scale_y_continuous(expand = c(0, 0), n.breaks = 3) +	
    ylab(ifelse(percent, "% rows \n missing:", "num rows \n missing:")) +	
    theme_linedraw(12) + 	
    theme(panel.grid.major.x = element_blank(),	
          panel.grid.minor.x = element_blank())	
  
  missing_by_pattern_plot <- 
    ggplot(na_count_by_pattern, aes(pattern, count/denom, alpha = none_missing)) +
    geom_col(fill = "cornflowerblue") +
    coord_flip() +
    scale_y_continuous(expand = c(0, 0), n.breaks = 3) +
    scale_alpha_manual(values = c(.7, 1)) +
    xlab("") +
    ylab(ifelse(percent, "% rows", "row count")) +
    guides(alpha = "none") +
    theme_linedraw(12) +
    theme(panel.grid.major.y = element_blank(), 
          panel.grid.minor.y = element_blank())
  
  if (percent) {	
    missing_by_column_plot <- missing_by_column_plot +
      scale_y_continuous(expand = c(0, 0), n.breaks = 5,
                         limits = c(0, 100))	
    missing_by_pattern_plot <- missing_by_pattern_plot +
      scale_y_continuous(expand = c(0, 0), n.breaks = 5,
                         limits = c(0, 100))	
  }	
  
  missing_by_column_plot + plot_spacer() + 	
    main_plot + missing_by_pattern_plot + 	
    plot_layout(widths = c(4, 1), heights = c(1, 4))
}