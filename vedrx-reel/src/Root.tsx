import { Composition } from 'remotion';
import { Reel } from './Reel';
import tl from './timeline.json';
export const RemotionRoot = () => (
  <Composition id="VedRxReel" component={Reel} durationInFrames={tl.total} fps={30} width={1080} height={1920} />
);
