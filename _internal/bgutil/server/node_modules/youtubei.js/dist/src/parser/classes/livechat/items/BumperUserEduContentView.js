import { YTNode } from '../../../helpers.js';
import Text from '../../misc/Text.js';
export default class BumperUserEduContentView extends YTNode {
    static type = 'BumperUserEduContentView';
    text;
    image_name;
    image_color;
    constructor(data) {
        super();
        this.text = Text.fromAttributed(data.text);
        this.image_name = data.image.sources[0].clientResource.imageName;
        this.image_color = data.image.sources[0].clientResource.imageColor;
    }
}
//# sourceMappingURL=BumperUserEduContentView.js.map