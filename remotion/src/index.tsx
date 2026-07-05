import React from 'react';
import { Composition } from 'remotion';

export const RemotionVideo: React.FC = () => null;

export const Video = () => (
  <Composition
    id="Video"
    component={ReminderVideo}
    durationInFrames={600}
    fps={30}
    width={1920}
    height={1080}
  />
);

function ReminderVideo() {
  return <div style={{ width: '100%', height: '100%', backgroundColor: '#0f172a', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Generated Video</div>;
}
