import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class EomSettingsDisclaimer extends YTNode {
    static type = 'EomSettingsDisclaimer';
    disclaimer;
    info_icon;
    usage_scenario;
    constructor(data) {
        super();
        this.disclaimer = new Text(data.disclaimer);
        this.info_icon = {
            icon_type: data.infoIcon.iconType
        };
        this.usage_scenario = data.usageScenario;
    }
}
//# sourceMappingURL=EomSettingsDisclaimer.js.map