from fixed_point import fixed_point

# Non-recursive.
@fixed_point(int)
def square(arg, unused_recurse):
    return arg * arg
print square(5)

# Normal, non-cyclic recursion.
@fixed_point(int)
def fibo(arg, recurse):
    if arg in (0, 1):
        return 1
    return recurse(arg - 1) + recurse(arg - 2)

print fibo(10)

# Cyclic
impliers = {
  1: [2], # 1 is implied by 2.
  2: [1],
  3: [1],
  4: [5],
  5: [6],
  6: [],
}
basic_truths = [6]

@fixed_point(bool)
def is_true(prop, _is_true):
  if prop in basic_truths:
    return True
  return any(_is_true(imp) for imp in impliers[prop])

for i in impliers:
  print '%s: %s' % (i, is_true(i))

# If P then P.
@fixed_point(bool)
def tautology(prop, _tautology):
  return _tautology(prop)

print tautology(1)

# If P then not P.
@fixed_point(bool)
def paradox(prop, _paradox):
  return not _paradox(prop)

# DO NOT SUBMIT: Detect this? Maybe notice some broken invariant about
# which edges are traversed during an evaluation of the inner
# function?
#print hard_paradox(1)
