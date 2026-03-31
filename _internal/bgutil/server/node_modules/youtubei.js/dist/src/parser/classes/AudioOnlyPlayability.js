import { YTNode } from '../helpers.js';
export default class AudioOnlyPlayability extends YTNode {
    static type = 'AudioOnlyPlayability';
    audio_only_availability;
    constructor(data) {
        super();
        this.audio_only_availability = data.audioOnlyAvailability;
    }
}
//# sourceMappingURL=AudioOnlyPlayability.js.map