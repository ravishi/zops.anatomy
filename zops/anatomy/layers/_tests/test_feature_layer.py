import pytest

from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.layers.feature import AnatomyFeature, AnatomyFeatureRegistry
from zops.anatomy.layers.tree import AnatomyTree


def test_file_not_found_error(datadir):
    feature = AnatomyFeature('createfile')
    feature.add_file_block(
        'invalid-id',
        """
            This is ALPHA.
        """
    )

    with pytest.raises(FileNotFoundError):
        _play_feature(feature, datadir)


def test_anatomy_feature(datadir):
    feature = AnatomyFeature('createfile')
    feature.create_file('fileid', 'filename.txt')
    feature.add_file_block('fileid', '# This file is generated by zops.anatomy.')

    _play_feature(feature, datadir)

    assert_file_contents(
        datadir + '/filename.txt',
        """
            # This file is generated by zops.anatomy.
        """
    )


def test_anatomy_feature_with_variable(datadir):
    feature = AnatomyFeature('CREATEFILE', variables={'code': 'ALPHA'})
    feature.create_file('filenametxt', 'filename.txt', variables={'code': 'BRAVO'})
    feature.add_file_block('filenametxt', '# This file {{ filenametxt.code }} from feature {{ CREATEFILE.code }}.')

    AnatomyFeatureRegistry.clear()
    assert AnatomyFeatureRegistry.tree() == []
    AnatomyFeatureRegistry.register('CREATEFILE', feature)
    assert AnatomyFeatureRegistry.tree() == [
        ('CREATEFILE', 'filenametxt', 'filename.txt')
    ]

    # Apply Feature
    tree = AnatomyTree()
    assert tree._AnatomyTree__variables == {}
    feature.apply(tree)
    assert tree._AnatomyTree__variables == {
        'CREATEFILE': {'code': 'ALPHA'},
        'filenametxt': {'code': 'BRAVO'},
    }
    tree.apply(datadir)

    assert_file_contents(
        datadir + '/filename.txt',
        """
            # This file BRAVO from feature ALPHA.
        """
    )


def test_anatomy_feature_from_yaml(datadir):
    AnatomyFeatureRegistry.clear()
    AnatomyFeatureRegistry.register_from_text(
        """
            anatomy-features:
              - name: CREATEFILE
                variables:
                  code: BRAVO
                commands:
                  - command: create-file
                    fileid: filenametxt
                    filename: filename.txt
                    variables:
                      code: ALPHA
                    contents: |
                       # This file is generated by zops.anatomy.
        """
    )
    assert AnatomyFeatureRegistry.tree() == [
        ('CREATEFILE', 'filenametxt', 'filename.txt')
    ]

    feature = AnatomyFeatureRegistry.get('CREATEFILE')
    assert feature.list_commands() == [
        """create_file(fileid=filenametxt, filename=filename.txt, variables={'code': 'ALPHA'})""",
        """add_file_block(fileid=filenametxt, contents=# This file is generated by zops.anatomy.\n)""",
    ]

    tree = _play_feature(feature, datadir)
    assert tree._AnatomyTree__variables == {
        'CREATEFILE': {'code': 'BRAVO'},
        'filenametxt': {'code': 'ALPHA'},
    }

    assert_file_contents(
        datadir + '/filename.txt',
        """
            # This file is generated by zops.anatomy.
        """
    )


def _play_feature(feature, directory, variables={}):
    """
    Could this be on AnatomyPlaybook.play?
    :param feature:
    :param directory:
    """
    tree = AnatomyTree()
    feature.apply(tree)
    tree.apply(directory, variables)
    return tree
