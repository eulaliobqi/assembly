# Rodar Trinity v2.15.2
Trinity \
  --seqType fq \
  --left  Unknown_CR776-001L0001_good_1.fq-001.gz \
  --right Unknown_CR776-001L0001_good_2.fq-002.gz \
  --max_memory 64G \
  --CPU 12 \
  --output ./trinity_mahanarva \
  --min_kmer_cov 2 \
  --min_contig_length 300 \
  --normalize_reads \
  --normalize_max_read_cov 50 \
  --SS_lib_type RF \
  --jaccard_clip \
  --verbose \
  2> trinity_mahanarva.log