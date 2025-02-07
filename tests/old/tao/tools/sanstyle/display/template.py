import re
from dataclasses import dataclass
from string import Template as _Template


@dataclass
class Tempalte:
    '''HTML 全局属性'''
    is_null: bool = False
    template: str = \
        '''<${tag} 
    accesskey="${accesskey}"
    autocapitalize="${autocapitalize}"
    autofocus="${autofocus}"
    class="${className}"
    contenteditable="${contenteditable}"
    dir="${dirName}"
    draggable="${draggable}"
    enterkeyhint="${enterkeyhint}"
    exportparts="${exportparts}"
    hidden="${hidden}"
    id="${id}"
    inputmode="${inputmode}"
    is="${isAction}"
    itemid="${itemid}"
    itemprop="${itemprop}"
    itemref="${itemref}"
    itemscope="${itemscope}"
    itemtype="${itemtype}"
    lang="${lang}"
    nonce="${nonce}"
    part="${part}"
    slot="${slot}"
    spellcheck="${spellcheck}"
    style="${style}"
    tabindex="${tabindex}"
    title="${title}"
    translate="${translate}" ${params}>
    ${content}</${tag}>'''.replace('\n', '').strip()

    def __post_init__(self):
        if self.is_null:
            template = self.template.replace('${content}</${tag}>', '')
        else:
            template = self.template
        self.template = re.sub(r"\s+", " ", template)

    def substitute(self, config):
        return _Template(self.template).substitute(config)