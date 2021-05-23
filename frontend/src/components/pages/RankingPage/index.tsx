import React from "react";
import {BASE_URL} from "../App";

import {TrackRow, UserTrack} from "./TrackRow";
import {ArtistRow, UserArtist} from "./ArtistRow";
import {JwtContext} from "../../../contexts/JwtContext";
import {ReplacePlaylistButton} from "../../projects/PlaylistReplaceButton";

interface ResponseTrack {
  id: string;
  name: string;
  artistIds: string[];
  blocked: boolean;
}

interface ResponseArtist {
  id: string;
  name: string;
  blocked: boolean;
}

interface Props {
}

interface State {
  userTracks: UserTrack[];
  userArtists: UserArtist[];
  inProgress: boolean;
}

export class RankingPage extends React.Component<Props, State> {
  static contextType = JwtContext;

  constructor(props: Props) {
    super(props);
    this.state = {
      userTracks: [],
      userArtists: [],
      inProgress: false,
    };
  }

  componentDidMount() {
    const jwt = this.context;
    fetch(BASE_URL + '/tracks_and_artists', {
      headers: {Authorization: `Bearer ${jwt}`}
    })
    .then(response => {
      return response.json()
    })
    .then(data => {
      const responseTracks: ResponseTrack[] = data['tracks'];
      const responseArtists: ResponseArtist[] = data['artists'];

      const userArtists: UserArtist[] = [];
      const userTracks: UserTrack[] = [];

      const userArtistMap: Record<string, UserArtist> = {};
      for (const ra of responseArtists) {
        const ua = new UserArtist(ra.id, ra.name, ra.blocked);
        userArtistMap[ua.id] = ua;
        userArtists.push(ua);
      }
      for (const rt of responseTracks) {
        const artists = [];
        for (const artistId of rt.artistIds) {
          artists.push(userArtistMap[artistId])
        }
        const ut = new UserTrack(rt.id, rt.name, artists, rt.blocked);
        userTracks.push(ut);
      }

      this.setState({
        userTracks: userTracks,
        userArtists: userArtists,
        inProgress: false,
      });
    })
    .catch(e => {
    })
  }

  render() {
    return (
        <div className="App">
          <ReplacePlaylistButton/>
          <div style={{display: "flex"}}>
            <div>
              <table>
                <thead>
                <tr>
                  <th>rank</th>
                  <th>name</th>
                  <th>artists</th>
                </tr>
                </thead>
                <tbody>
                {this.state.userTracks.map((userTrack, i) => {
                  return <TrackRow
                      rank={i + 1}
                      userTrack={userTrack}
                      updateParent={() => this.forceUpdate()}
                      key={userTrack.id}/>
                })}
                </tbody>
              </table>
            </div>
            <div>
              <table>
                <thead>
                <tr>
                  <th>name</th>
                </tr>
                </thead>
                <tbody>
                {this.state.userArtists.map((userArtist) => {
                  return <ArtistRow
                      userArtist={userArtist}
                      updateParent={() => this.forceUpdate()}
                      key={userArtist.id}/>
                })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
    )
  }
}

