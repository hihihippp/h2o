source('./Utils/h2oR.R')

Log.info("======================== Begin Test ===========================")
view_max <- 10000 #maximum returned by Inspect.java


test.tail.numeric <- function(conn) {
  Log.info("Importing USArrests.csv data...")
  arrests.hex = h2o.importFile.VA(conn, "./smalldata/pca_test/USArrests.csv", "arrests.hex")
  
  Log.info("Check that tail works...")
  tail(arrests.hex)
  
  tail_ <- tail(arrests.hex)
  
  Log.info("Check that we get a data frame back from the tail(hex)")
  expect_that(tail_, is_a("data.frame"))
  
  tail_2 <- tail(USArrests)
  rownames(tail_2) <- 1:nrow(tail_2) #remove state names from USArrests
  
  Log.info("Check that the tail of the dataset is the same as what R produces: ")
  Log.info("tail(USArrests)")
  Log.info(tail_2)
  Log.info("tail(arrests.hex)")
  Log.info(tail_)
  expect_that(tail_, equals(tail_2))
  if( nrow(arrests.hex) <= view_max) {
    Log.info("Try doing tail w/ n > nrows(data). Should do same thing as R (returns all rows)")
    Log.info(paste("Data has ", paste(nrow(arrests.hex), " rows",sep=""),sep=""))
    tail_max <- tail(arrests.hex,nrow(arrests.hex) + 1)
  }
  Log.info("End of test.")
}

conn <- new("H2OClient", ip=myIP, port=myPort)

tryCatch(test_that("tailTests",test.tail.numeric(conn)), error = function(e) FAIL(e))
PASS()

