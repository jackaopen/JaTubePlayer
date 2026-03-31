import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
export default class UpdateDescriptionAction extends YTNode {
    static type = 'UpdateDescriptionAction';
    description;
    constructor(data) {
        super();
        this.description = new Text(data.description);
    }
}
//# sourceMappingURL=UpdateDescriptionAction.js.map