import { Parser, ContinuationCommand } from '../index.js';
import { InnertubeError } from '../../utils/Utils.js';
import MediaInfo from '../../core/mixins/MediaInfo.js';
export default class ShortFormVideoInfo extends MediaInfo {
    #watch_next_continuation;
    watch_next_feed;
    current_video_endpoint;
    player_overlays;
    constructor(data, actions, cpn, reel_watch_sequence_response) {
        super(data, actions, cpn);
        if (reel_watch_sequence_response) {
            const reel_watch_sequence = Parser.parseResponse(reel_watch_sequence_response.data);
            if (reel_watch_sequence.entries)
                this.watch_next_feed = reel_watch_sequence.entries;
            if (reel_watch_sequence.continuation_endpoint)
                this.#watch_next_continuation = reel_watch_sequence.continuation_endpoint?.as(ContinuationCommand);
        }
    }
    async getWatchNextContinuation() {
        if (!this.#watch_next_continuation)
            throw new InnertubeError('Continuation not found');
        const response = await this.actions.execute('/reel/reel_watch_sequence', {
            sequenceParams: this.#watch_next_continuation.token,
            parse: true
        });
        if (response.entries)
            this.watch_next_feed = response.entries;
        this.#watch_next_continuation = response.continuation_endpoint?.as(ContinuationCommand);
        return this;
    }
    /**
     * Checks if continuation is available for the watch next feed.
     */
    get wn_has_continuation() {
        return !!this.#watch_next_continuation;
    }
}
//# sourceMappingURL=ShortFormVideoInfo.js.map