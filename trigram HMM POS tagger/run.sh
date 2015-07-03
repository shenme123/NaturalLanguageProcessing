python count freqs.py ner train.dat > ner.counts
python question4.py ner_train.dat ner_dev.dat > tagging_baseline
python eval_ne_tagger.py ner_dev.key tagging_baseline
python question5.py ner.counts_rare emission_prob ner_dev.dat wordlist_5_or_more > tagging_rare
python eval_ne_tagger.py ner_dev.key tagging_rare
python question6.py ner_train.dat ner_dev.dat > tagging_sets
python eval_ne_tagger.py ner_dev.key tagging_sets
python question6_2.py ner_train.dat ner_dev.dat > tagging_sets_2
python eval_ne_tagger.py ner_dev.key tagging_sets_2