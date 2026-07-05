import React from 'react';
import {Composition} from 'remotion';

export const RemotionVideo: React.FC = () => (
  <Composition
    id="Video"
    component={() => <div>Generated video</div>}
    durationInFrames={600}
    fps={30}
    width={1920}
    height={1080}
  />
);