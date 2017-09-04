# -*- coding: utf-8 -*-
import os
from zerotk.zops import Console

import click


ANATOMY_FILENAME = 'anatomy.yml'


click.disable_unicode_literals_warning = True


@click.group('anatomy')
def main():
    pass


@main.command('tree')
@click.pass_context
def tree(ctx):
    from .layers.feature import AnatomyFeatureRegistry
    from .layers.playbook import AnatomyPlaybook

    AnatomyFeatureRegistry.register_from_file(
        '/home/kaniabi/Projects/axado/anatomy/anatomy-features.yml'
    )

    tree = AnatomyFeatureRegistry.tree()
    tree = sorted([('/' not in filename, filename, fileid, feature) for (feature, fileid, filename) in tree])
    for _priority, i_filename, i_fileid, i_feature in tree:
        Console.item(i_filename)


@main.command()
@click.argument('directories', nargs=-1)
@click.pass_context
def apply(ctx, directories):
    """
    Apply templates.
    """
    from .layers.feature import AnatomyFeatureRegistry
    from .layers.playbook import AnatomyPlaybook

    AnatomyFeatureRegistry.register_from_file(
        '/home/kaniabi/Projects/axado/anatomy/anatomy-features.yml'
    )

    if not directories:
        directories = ('.',)
    directories = [os.path.abspath(i) for i in directories]

    for i_directory in directories:
        Console.title(i_directory)
        anatomy_playbook = AnatomyPlaybook.from_file(i_directory + '/anatomy-playbook.yml')
        anatomy_playbook.apply(i_directory)
