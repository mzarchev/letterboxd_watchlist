library(shiny)
library(DT)
library(here)

df_movies <-
  read.csv(here("data", "df_formatted.csv"))

df_movies_formatted <-
  df_movies |>
  dplyr::select(Poster, Title, Year, Genres, `Stream on` = Stream.on,
                `RT score` = RT.score, `Letterboxd score` = Letterboxd.score,
                Director, Cast, Language) |>
  dplyr::mutate(Poster = paste0("<img src='", Poster, "'height='200', style='border-radius: 10%;'></img>"))


# Define UI for application that draws a histogram
ui <- fluidPage(

    br(), br(),

    fluidRow(column(9, offset = .2, titlePanel("Milan's watchlist yall")),
             column(3, tags$a(href = "https://letterboxd.com/mzarchev/watchlist/",
                              img(height = 80, width = 80,
                                  style = "border-radius: 50%;",
                                  src = "https://github.com/mzarchev/utils/blob/main/avtr-0-1000-0-1000-crop.jpg?raw=true"
                           )))),
    br(), br(),
    
    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
            sliderInput("year",
              "Release date:",
              min = min(df_movies$Year, na.rm = T),
              max = max(df_movies$Year, na.rm = T),
              value = median(df_movies$Year, na.rm = T),
              round = T,
              sep ="",
              ticks = F),
            width = 2,
            position = "left"
        ), 

        # Show a plot of the generated distribution
        mainPanel(
           div(DT::DTOutput("tbl_movies"),
               style = "font-size:105%"),
           width = 8
        )
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
  
  

    output$tbl_movies <- DT::renderDataTable({
        
      datatable(df_movies_formatted,
                # dplyr::select(df_movies, -genres_list),
                escape = FALSE,
                selection = "single",
                # width = "100%",
                options = list(
                  pageLength = 5,
                  scrollX = T
                  # columnDefs = list(list(width = '50px',
                                         # scrollX = T,
                                         # scrollY = '800px',
                                         # targets = "_all"))
                  )
                )
    })
}

# Run the application 
shinyApp(ui = ui, server = server)
# 
# 
# options = list(autoWidth = TRUE,
#                columnDefs = list(list(width = '100px',
#                                       targets = "_all")))