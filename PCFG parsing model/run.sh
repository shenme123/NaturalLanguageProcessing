python count_cfg_freq.py parse_train.dat > cfg.counts
python question4.py > parse_train_rev.dat
python count_cfg_freq.py parse_train_rev.dat > cfg_rare.counts

python question5.py > parse_dev_result
python eval_parser.py parse_dev.key parse_dev_result

python count_cfg_freq.py parse_train_vert.dat > cfg_vert.counts
python question4_.py > parse_train_vert_rev.dat
python count_cfg_freq.py parse_train_vert_rev.dat > cfg_vert_rare.counts
python question5_.py > parse_dev_vert_result
python eval_parser.py parse_dev.key parse_dev_vert_result