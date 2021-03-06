import pandas as pd
from numpy import nonzero

from scattertext.TermDocMatrix import TermDocMatrix


class Corpus(TermDocMatrix):
	def __init__(self,
	             X, mX, y,
	             term_idx_store,
	             category_idx_store,
	             metadata_idx_store,
	             raw_texts,
	             unigram_frequency_path=None):
		'''
		Parameters
		----------
		X : csr_matrix
			term document matrix
		mX : csr_matrix
			metadata-document matrix
		y : np.array
			category index array
		term_idx_store : IndexStore
			Term indices
		category_idx_store : IndexStore
			Catgory indices
		metadata_idx_store : IndexStore
		  Document metadata indices
		raw_texts : np.array or pd.Series
			Raw texts
		unigram_frequency_path : str or None
			Path to term frequency file.
		'''
		TermDocMatrix.__init__(self, X, mX, y,
		                       term_idx_store,
		                       category_idx_store,
		                       metadata_idx_store,
		                       unigram_frequency_path)
		self._raw_texts = raw_texts

	def get_texts(self):
		'''
		Returns
		-------
		pd.Series, all raw documents
		'''
		return self._raw_texts

	def search(self, ngram):
		'''
		Parameters
		----------
		ngram str or unicode, string to search for

		Returns
		-------
		pd.DataFrame, {'texts': <matching texts>, 'categories': <corresponding categories>}

		'''
		mask = self._document_index_mask(ngram)
		return pd.DataFrame({
			'text': self.get_texts()[mask],
			'category': [self._category_idx_store.getval(idx)
			             for idx in self._y[mask]]
		})

	def search_index(self, ngram):
		"""
		Parameters
		----------
		ngram str or unicode, string to search for

		Returns
		-------
		np.array, list of matching document indices
		"""
		return nonzero(self._document_index_mask(ngram))[0]

	def _document_index_mask(self, ngram):
		idx = self._term_idx_store.getidxstrict(ngram.lower())
		mask = (self._X[:, idx] > 0).todense().A1
		return mask

	def _term_doc_matrix_with_new_X(self, new_X, new_term_idx_store):
		return Corpus(X=new_X,
		              mX=self._mX,
		              y=self._y,
		              term_idx_store=new_term_idx_store,
		              category_idx_store=self._category_idx_store,
		              metadata_idx_store=self._metadata_idx_store,
		              raw_texts=self.get_texts(),
		              unigram_frequency_path=self._unigram_frequency_path)
