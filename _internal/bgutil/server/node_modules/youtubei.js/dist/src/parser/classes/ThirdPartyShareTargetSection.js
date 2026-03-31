import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import ShareTarget from './ShareTarget.js';
export default class ThirdPartyShareTargetSection extends YTNode {
    static type = 'ThirdPartyShareTargetSection';
    share_targets;
    constructor(data) {
        super();
        this.share_targets = Parser.parseArray(data.shareTargets, ShareTarget);
    }
}
//# sourceMappingURL=ThirdPartyShareTargetSection.js.map