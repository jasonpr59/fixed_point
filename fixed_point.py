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
      logger.cache_hit(arg, cached_result)
      return cached_result

    def recurse(child):
      """Note that the current caller depends on the child, then recurse normally."""
      logger.recursed(arg, child)
      callers_of[child].add(arg)
      return modified_func(child)

    # Keep on chasing quietness around until it settles everywhere.
    loops = 0
    while arg not in quiet:
      # Claim it is quiet just before calling the inner_func (and risking
      # recursion). This way, if a cycle occurs, we won't loop infinitely.
      quiet.add(arg)

      logger.computing(arg, loops)
      new_result = inner_func(arg, recurse)
      logger.computed(arg, new_result)
      if cached_values[arg] != new_result:
        logger.cache_update(arg, new_result)
        cached_values[arg] = new_result
        # When a node's value changes, call into doubt the value of everyone who
        # depends on it.
        # We are returning the new, changed value to the caller, so it might
        # seem like we don't need to cast doubt on the caller.  But, if the
        # caller called this node twice (e.g. something like
        # f(x) = f(x-1) + f(x-1)), and the value change was only detected on the
        # second call, then the caller would still need a recomputation.
        quiet.difference_update(callers_of[arg])
        for caller in callers_of[arg]:
          logger.invalidate(caller)
      else:
        logger.verified(arg, new_result)
      loops += 1

    return new_result
  return modified_func

class _AbstractLogger(object):

  def verified(self, arg, value):
    """Log that we computed f(arg) = value, the same as was cached.

    In this case, there's no need to invalidate the callers of f(arg).
    """
    self._log('VERIFIED', (arg, value))

  def cache_update(self, arg, value):
    """Log that we updated the cated entry for f(arg) = value."""
    self._log('CACHE_UPDATE', (arg, value))

  def cache_hit(self, arg, value):
    """Log that we answered f(arg) by returning value from the cache."""
    self._log('CACHE_HIT', (arg, value))

  def invalidate(self, arg):
    """Log that we cast doubt on f(arg), i.e. removed it from the quiet set."""
    self._log('INVALIDATE', arg)

  def recursed(self, parent, child):
    """Log that f(parent) calls f(child)."""
    self._log('RECURSED', (parent, child))

  def computing(self, arg, loops):
    """Log that we are calling inner_func for f(arg).
    
    Args:
      arg: The argument to the target function.
      loops: Zero-indexed invocation number of inner_func within this
             computation of f(arg).
    """
    self._log('COMPUTING', (arg, loops))

  def computed(self, arg, value):
    """Log that we computed that f(arg) = value by calling inner_func."""
    self._log('COMPUTED', (arg, value))

class Logger(_AbstractLogger):
  def __init__(self):
    self.log = []

  def _log(self, event_type, details):
    self.log.append((event_type, details))

  def clear(self):
    self.log = []

  def pretty_print(self):
    depth = 0
    for event, details in self.log:
      delta = 0
      if event == 'CACHE_HIT':
        msg = 'cache hit: f(%r) = %r' % details
      elif event == 'CACHE_UPDATE':
        msg = 'cache update: f(%r) = %r' % details
      elif event == 'RECURSED':
        msg =  'f(%r) -> f(%r)' % details
      elif event == 'COMPUTING':
        delta = 1
        msg = 'Computing f(%r) [loop #%d]:' % details
      elif event == 'COMPUTED':
        delta = -1
        msg = 'Computed f(%r) = %r' % details
      elif event == 'INVALIDATE':
        msg = 'Invalidating f(%r)' % details
      elif event == 'VERIFIED':
        msg = 'Verified: f(%r) = %r' % details
      else:
        raise ValueError('Unknown event %s', event)

      print '    ' * depth + msg
      depth += delta


class NopLogger(_AbstractLogger):

  def _log(self, event_type, details):
    pass
