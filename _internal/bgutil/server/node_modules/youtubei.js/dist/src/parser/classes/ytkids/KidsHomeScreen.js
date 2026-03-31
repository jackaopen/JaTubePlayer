import { Parser } from '../../index.js';
import AnchoredSection from './AnchoredSection.js';
import { YTNode } from '../../helpers.js';
export default class KidsHomeScreen extends YTNode {
    static type = 'kidsHomeScreen';
    anchors;
    constructor(data) {
        super();
        this.anchors = Parser.parseArray(data.anchors, AnchoredSection);
    }
}
//# sourceMappingURL=KidsHomeScreen.js.map