import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
export default class UpdateTitleAction extends YTNode {
    static type = 'UpdateTitleAction';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=UpdateTitleAction.js.map