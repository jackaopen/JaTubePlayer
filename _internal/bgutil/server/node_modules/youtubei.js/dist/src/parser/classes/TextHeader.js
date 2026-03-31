import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class TextHeader extends YTNode {
    static type = 'TextHeader';
    title;
    style;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.style = data.style;
    }
}
//# sourceMappingURL=TextHeader.js.map