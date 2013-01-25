# builder.py calls functions in this file names ${recipe}_recipe, where ${recipe}
# is taken from packages.yml
import os

def standard_recipe(ctx, attrs, buildspec):
    buildspec['build']['script'].append([ # appending a list creates a sub-scope
        ['cd', 'src'],
        ['PATH=%s' % os.environ['PATH']],
        ['PYTHONHPC_PREFIX=${ARTIFACT}'],
        ['sh', '../configure'],
        ['make'],
        ['make', 'install']])
