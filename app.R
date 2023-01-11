library(shiny)
library(DT)
library(here)

# Import data
df_movies <- read.csv(here("data", "df_formatted.csv"))
unique_genres <- read.csv(here("data", "unique_genres.csv"))$genres

df_movies_formatted <-
  df_movies |>
  dplyr::select(Title, Year, Genres, Stream = Stream.on,
                `<img src ='https://github.com/mzarchev/utils/blob/main/rt.jpg?raw=true'height=40, style='border-radius: 10%;'></img>` = RT.score,
                `<img src ='https://github.com/mzarchev/utils/blob/main/lb.png?raw=true'height=40, style='border-radius: 10%;'></img>` = Letterboxd.score,
                Runtime, Director, Description,
                poster_url = Poster, Cast, Language) |>
  dplyr::mutate(Poster = paste0("<img src='", poster_url, "'height='200', style='border-radius: 10%;'></img>"),
                .before = Title) |>
  dplyr::mutate(Runtime = hms::hms(minutes = Runtime)) 


## --- UI ---
ui <- fluidPage( 
  
  br(),
  
  fluidRow(column(9, offset = .2, titlePanel("Milan's watchlist")),
           column(3, tags$a(href = "https://letterboxd.com/mzarchev/watchlist/",
                            img(height = 80, width = 80,
                                style = "border-radius: 50%;",
                                src = "https://github.com/mzarchev/utils/blob/main/avtr-0-1000-0-1000-crop.jpg?raw=true"
                         )))),
  tags$h4("Never paying for premuim"),
  br(), br(),
  
  # Sidebar with a slider input for number of bins 
  sidebarLayout(
      sidebarPanel(
          sliderInput("year",
            label = "Release date:",
            min = min(df_movies$Year, na.rm = T),
            max = max(df_movies$Year, na.rm = T),
            value = c(min(df_movies$Year, na.rm = T),
                      max(df_movies$Year, na.rm = T)),
            round = T,
            sep ="",
            ticks = F),
          checkboxGroupInput("genres",
            label = "Include:", 
            choices = unique_genres,
            selected = NA,
            inline = F
            ),
          width = 2,
          position = "left"
      ), 

      # Show a plot of the generated distribution
      mainPanel(
         div(DT::DTOutput("tbl_movies"),
             style = "font-size:105%"),
         br(), br(), br(),
         fluidRow(
           column(6, htmlOutput("selected_poster")),
           column(6, htmlOutput("selected_description")),
         ),
         # div(DT::DTOutput("row_selected"),
         #     style = "font-size:105%"),
         width = 8
      )
  )
)

### --- Server ---
server <- function(input, output){
    

  # Filter according to inputs
  filter_movies <- function(){
    selected_genres <- paste(input$genres, collapse = "|")
    selected_genres <- paste0(selected_genres, "|^$")
    
    dplyr::filter(df_movies_formatted,
                  Year >= input$year[1],
                  Year <= input$year[2],
                  stringr::str_detect(Genres, selected_genres),
                  )
  }
  # Reactive
  reactive_movie_df <- reactive({filter_movies()})

  # Output interactive DT table
  output$tbl_movies <- DT::renderDataTable({
    DT::datatable(reactive_movie_df(),
                  escape = FALSE,
                  selection = "single",
                  options = list(pageLength = 5,
                                 scrollX = T,
                                 columnDefs = list(list(visible = FALSE,
                                                        targets = c("Genres",
                                                                    "Cast",
                                                                    "Description",
                                                                    "Language",
                                                                    "poster_url")))
                                )
                  )
  })
  
  # Get the selected DT row
  select_row <- function(){
    reactive_movie_df()[input[["tbl_movies_rows_selected"]], ]
  }
  reactive_selected <- reactive({select_row()})

  output$selected_poster <- renderText(paste0("<img src='",
                                              dplyr::pull(reactive_selected(), poster_url),
                                              "'height=400, style='border-radius: 10%;'>"))
  
  output$selected_description <- renderText(paste0("<h1>",
                                            dplyr::pull(reactive_selected(), Title),
                                            "</h1><h3>",
                                            dplyr::pull(reactive_selected(), Year),
                                            "</h3><p>",
                                            dplyr::pull(reactive_selected(), Description),
                                            "</p><h5>",
                                            dplyr::pull(reactive_selected(), Stream)
                                            ))
  
 
  
}

shinyApp(ui = ui, server = server)
# observeEvent(input$show_row,
#              {print(input[["tbl_movies_rows_selected"]])
#                # print(reactive_movie_df()[input[["tbl_movies_rows_selected"]], ]),
#                print(dplyr::pull(reactive_selected(), Poster))
#              })