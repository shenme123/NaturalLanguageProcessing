python question4.py tag.model tag_dev.dat > tag_dev_q4.out
python eval_tagger.py tag_dev.key tag_dev_q4.out

python question5.py tag_train.dat tag_dev.dat > tag_dev_q5.out
python eval_tagger.py tag_dev.key tag_dev_q5.out

python question6_1.py tag_train.dat tag_dev.dat > tag_dev_q6_1.out
python eval_tagger.py tag_dev.key tag_dev_q6_1.out

python question6_2.py tag_train.dat tag_dev.dat > tag_dev_q6_2.out
python eval_tagger.py tag_dev.key tag_dev_q6_2.out

python question6_3.py tag_train.dat tag_dev.dat > tag_dev_q6_3.out
python eval_tagger.py tag_dev.key tag_dev_q6_3.out