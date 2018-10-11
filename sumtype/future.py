from .sumtype import sumtype as current_sumtype

__all__ = ['sumtype']


def error_deprecated():
	raise TypeError('This feature is deprecated and will be removed in a future release')


class future_sumtype(current_sumtype, _process_class=False):
	_options_for_generated_classes=dict(constants=True)

	@classmethod
	def with_constructors(cls, *_args, **_kwargs):
		error_deprecated()

	@classmethod
	def untyped_with_constructors(cls, *_args, **_kwargs):
		error_deprecated()

sumtype = future_sumtype

