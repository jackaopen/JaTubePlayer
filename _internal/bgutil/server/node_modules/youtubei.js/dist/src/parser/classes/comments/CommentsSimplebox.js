import { YTNode } from '../../helpers.js';
import Text from '../misc/Text.js';
import Thumbnail from '../misc/Thumbnail.js';
export default class CommentsSimplebox extends YTNode {
    static type = 'CommentsSimplebox';
    simplebox_avatar;
    simplebox_placeholder;
    constructor(data) {
        super();
        this.simplebox_avatar = Thumbnail.fromResponse(data.simpleboxAvatar);
        this.simplebox_placeholder = new Text(data.simpleboxPlaceholder);
    }
}
//# sourceMappingURL=CommentsSimplebox.js.map