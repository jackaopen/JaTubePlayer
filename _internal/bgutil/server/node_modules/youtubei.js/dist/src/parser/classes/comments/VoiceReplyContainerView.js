import { YTNode } from '../../helpers.js';
import Text from '../misc/Text.js';
export default class VoiceReplyContainerView extends YTNode {
    static type = 'VoiceReplyContainerView';
    voice_reply_unavailable_text;
    transcript_text;
    constructor(data) {
        super();
        this.voice_reply_unavailable_text = Text.fromAttributed(data.voiceReplyUnavailableText);
        this.transcript_text = Text.fromAttributed(data.transcriptText);
    }
}
//# sourceMappingURL=VoiceReplyContainerView.js.map