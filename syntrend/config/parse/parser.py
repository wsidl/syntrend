from ruamel.yaml import YAML, ScalarNode
from syntrend.config import model
import re

yaml = YAML(typ='safe')


RE_INCLUDE_REF = re.compile(r'^(.*?)(?: (\d*))?')
RE_SYNTREND_REF = re.compile(r'^(.*?)(?:::(.*))?$')
EXC_SYNTREND_TAG = ValueError(
    'Invalid "!syntrend" reference',
    {
        'Provided': '!syntrend/name',
        'Reference Tag': '!syntrend/ref::(reference_name)',
        'Project Root Tag': '!syntrend/root',
        'Position Tag': '!syntrend/pos::(dot-separated path)',
    },
)


def yaml_include(_, node):
    if not (match := RE_INCLUDE_REF.fullmatch(node.value)):
        raise ValueError(
            'Invalid "!include" reference', {'Value': node.value}
        ) from None
    path_ref, index = match.groups()
    return model.DocumentLink(
        model.DOCUMENTS.current_file.parent.joinpath(path_ref), int(index or 0)
    )


TAG_MAP = {
    'ref': lambda ref: (
        ScalarNode('tag:yaml.org,2002:str', model.constants.OBJ_REF_TAG),
        ScalarNode('tag:yaml.org,2002:str', ref),
    ),
    'root': lambda _: (
        ScalarNode('tag:yaml.org,2002:str', model.constants.OBJ_POS_TAG),
        ScalarNode('tag:yaml.org,2002:str', '.'),
    ),
    'pos': lambda pos: (
        ScalarNode('tag:yaml.org,2002:str', model.constants.OBJ_POS_TAG),
        ScalarNode('tag:yaml.org,2002:bool', pos),
    ),
}


def syntrend_tag_constructor(constructor: YAML.constructor, suffix: str, node):
    if not (match := RE_SYNTREND_REF.fullmatch(suffix)):
        exception = EXC_SYNTREND_TAG
        exception.args[1]['Provided'] = f'!syntrend/{suffix}'
        raise exception from None
    func_name, ref = match.groups()
    if func_name not in {'ref', 'root', 'pos'}:
        exception = EXC_SYNTREND_TAG
        exception.args[1]['Provided'] = f'!syntrend/{suffix}'
        raise exception from None

    node.value.insert(0, TAG_MAP[func_name](ref))
    return constructor.construct_mapping(node)


yaml.constructor.add_constructor('!include', yaml_include)
yaml.constructor.add_multi_constructor('!syntrend/', syntrend_tag_constructor)
# TODO(ws): Test include and syntrend constructors
