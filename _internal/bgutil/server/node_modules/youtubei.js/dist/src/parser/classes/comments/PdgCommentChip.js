import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
export default class PdgCommentChip extends YTNode {
    static type = 'PdgCommentChip';
    text;
    color_pallette;
    icon_type;
    constructor(data) {
        super();
        this.text = new Text(data.chipText);
        this.color_pallette = {
            background_color: data.chipColorPalette?.backgroundColor,
            foreground_title_color: data.chipColorPalette?.foregroundTitleColor
        };
        if (Reflect.has(data, 'chipIcon') && Reflect.has(data.chipIcon, 'iconType')) {
            this.icon_type = data.chipIcon.iconType;
        }
    }
}
//# sourceMappingURL=PdgCommentChip.js.map