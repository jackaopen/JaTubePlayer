import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class TitleAndButtonListHeader extends YTNode {
    static type = 'TitleAndButtonListHeader';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=TitleAndButtonListHeader.js.map