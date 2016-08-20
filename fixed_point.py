import collections

def fixed_point(zero_factory, logger=None):
  log = logger if logger else NopLogger()
  return lambda inner_func: _decorator_instance(inner_func, zero_factory, log)

def _decorator_instance(inner_func, zero_factory, logger):
  quiet = set()
  callers_of = collections.defaultdict(set)
  cached_values = collections.defaultdict(zero_factory)

  def modified_func(arg):
    if arg in quiet:
      cached_result = cached_values[arg]
      logger.cached_result(arg, cached_result)
      return cached_result
    # Claim it is quiet just before calling the inner_func (and risking recursion).
    # This way, if a cycle occurs, it execution will terminate.
    quiet.add(arg)

    def recurse(child):
      """Note that the current caller depends on the child, then recurse normally."""
      logger.recursed(arg, child)
      callers_of[child].add(arg)
      return modified_func(child)

    # Keep on chasing quietness around until it settles everywhere.
    logger.computing(arg)
    new_result = inner_func(arg, recurse)
    logger.computed(arg, new_result)
    while new_result != cached_values[arg]:
      cached_values[arg] = new_result
      # When a node's value changes, call into doubt the value of everyone who depends on it.
      quiet.difference_update(callers_of[arg])
      logger.computing(arg)
      new_result = inner_func(arg, recurse)
      logger.computed(arg, new_result)
    return new_result
  return modified_func

class _AbstractLogger(object):

  def cached_result(self, arg, value):
    self._log('CACHED_RESULT', (arg, value))

  def recursed(self, parent, child):
    self._log('RECURSED', (parent, child))

  def computing(self, arg):
    self._log('COMPUTING', arg)

  def computed(self, arg, value):
    self._log('COMPUTED', (arg, value))

class Logger(_AbstractLogger):
  def __init__(self):
    self.log = []

  def _log(self, event_type, details):
    self.log.append((event_type, details))

  def clear(self):
    self.log = []

  def pretty_print(self):
    for entry in self.log:
      print '%s: %s' % entry

class NopLogger(_AbstractLogger):

  def _log(self, event_type, details):
    pass
