import collections

def log(msg):
  if False:
    print msg

def fixed_point(zero_factory):
    return lambda inner_func: _decorator_instance(inner_func, zero_factory)

def _decorator_instance(inner_func, zero_factory):
  quiet = set()
  callers_of = collections.defaultdict(set)
  cached_values = collections.defaultdict(zero_factory)

  def modified_func(arg):
    if arg in quiet:
      log('Cached f(%s) = %s' % (arg, cached_values[arg]))
      return cached_values[arg]
    # Claim it is quiet just before calling the inner_func (and risking recursion).
    # This way, if a cycle occurs, it execution will terminate.
    quiet.add(arg)

    def recurse(child):
      """Note that the current caller depends on the child, then recurse normally."""
      log('%s calls %s' % (arg, child))
      callers_of[child].add(arg)
      return modified_func(child)

    # Keep on chasing quietness around until it settles everywhere.
    new_result = inner_func(arg, recurse)
    while new_result != cached_values[arg]:
      cached_values[arg] = new_result
      # When a node's value changes, its dependors' values are called into doubt.
      quiet.difference_update(callers_of[arg])
      log("Computing %s" % arg)
      new_result = inner_func(arg, recurse)
    return new_result
  return modified_func
