# Go-with-NLP
## Data
### Collection
  * download from : 
  * file type : .sgf
### Preprocessing :
  * change encode mode to UTF-8 (iconv)
  * convert simplified Chinese to traditional Chinese (opencc)
  * discard information about extra analysis
  * integrate the beginning style of the sentences
  * add the labels : \</s\>, \</end\>, \<step\>, \<step-N\>
### Structure / Encoding
  * each board maps to one comment
## Model
  * CNN
  * LSTM
