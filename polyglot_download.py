from polyglot.downloader import downloader

download_dir = '/root/polyglot_data'
"""
The Embeddings are necessary for the ner2 task, however the downloader doesn't download
them automatically and doesn't provide a list of language codes of necessary embeddings,
but only names. The embeddings for languages supported by spacy are not downloaded.
"""
embeddings = ['embeddings2.en', 'embeddings2.de', 'embeddings2.ar', 'embeddings2.bg',
              'embeddings2.ca', 'embeddings2.cs', 'embeddings2.da',  'embeddings2.el',
              'embeddings2.et', 'embeddings2.fa', 'embeddings2.fi', 'embeddings2.he',
              'embeddings2.hi', 'embeddings2.hr', 'embeddings2.hu', 'embeddings2.id',
              'embeddings2.ja', 'embeddings2.ko', 'embeddings2.lt', 'embeddings2.lv',
              'embeddings2.ms', 'embeddings2.no', 'embeddings2.ro', 'embeddings2.sk',
              'embeddings2.sl', 'embeddings2.sr', 'embeddings2.sv', 'embeddings2.th',
              'embeddings2.tl', 'embeddings2.tr', 'embeddings2.uk', 'embeddings2.vi',
              'embeddings2.zh']

downloader.download("TASK:ner2", download_dir=download_dir)
downloader.download(embeddings,  download_dir=download_dir)
