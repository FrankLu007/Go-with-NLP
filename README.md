# Go-with-NLP
## Data
### Collection
  * download from : 
  * file type : .sgf
### Preprocessing :
  * change encode mode to UTF-8 (iconv)
  * convert simplified Chinese to traditional Chinese (opencc)
  * discard information about extra analysis
  * remove meanless or short (len < 3) sentence
  * integrate the beginning style of the sentences
  * add the labels : \</s\>, \</end\>, \</step\>, \</step-N\>, \</color\>, \</rcolor\>
### Feature / Encoding
  * each board maps to one comment
  * feature : move, threat(, score)
  * move feature : previous N step (default : 8)
  * threat feature : categorize 1~S+ lives(chi) of each stone group (default : 8)
  * score feature : the score of both side
## Model
  * Encoder : BiLSTM
  * Decoder : Attention & LSTM
## Usage
### Data Collection & Preprocessing
  ```
  ./data_collection.sh
  ```
### Train
  ```
  python3 train.py
  --gpu [int]
  --epoch [int]
  --batch_size [int]
  --sentence_length [int]
  --learning_rate [float]
  --test [float]               proportion of test data
  --validdation [float]        proportion of validation data
  --input_board [file]
  --input_comment [file]
  --embedding_file [file]
  --weight [file]              
  ```
