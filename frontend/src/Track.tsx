import React from "react";
import {BASE_URL} from './App'

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


class UserArtist {
  id: string;
  name: string;
  blocked: boolean;

  constructor(id: string, name: string, blocked: boolean) {
    this.id = id;
    this.name = name;
    this.blocked = blocked;
  }

  isBlocked() {
    return this.blocked;
  }
}

class UserTrack {
  id: string;
  name: string;
  userArtists: UserArtist[];
  blocked: boolean;

  constructor(id: string, name: string, userArtists: UserArtist[], blocked: boolean) {
    this.id = id;
    this.name = name;
    this.userArtists = userArtists;
    this.blocked = blocked;
  }

  isBlocked(): boolean {
    return this.blocked || this.userArtists.some((v) => v.blocked);
  }
}

interface TrackRowProps {
  rank: number;
  userTrack: UserTrack;
  updateParent: Function;
}

interface CommonState {
  inProgress: boolean;
}

class TrackRow extends React.Component<TrackRowProps, CommonState> {
  constructor(props: TrackRowProps) {
    super(props);
    this.state = {inProgress: false}
  }

  block(trackId: string) {
    if (this.state.inProgress) {
      return;
    }
    this.setState({inProgress: true})
    const url = `${BASE_URL}/tracks/${trackId}/block`;
    fetch(url, {method: 'POST'}).then(() => {
      this.props.userTrack.blocked = true;
      this.setState({inProgress: false})
      this.props.updateParent();
    })
  }

  unblock(trackId: string) {
    if (this.state.inProgress) {
      return;
    }
    this.setState({inProgress: true})
    const url = `${BASE_URL}/tracks/${trackId}/unblock`;
    fetch(url, {method: 'POST'}).then(() => {
      this.props.userTrack.blocked = false;
      this.setState({inProgress: false})
      this.props.updateParent();
    })
  }

  render() {
    const userTrack = this.props.userTrack;
    let button;
    if (userTrack.blocked) {
      button = <button
          disabled={this.state.inProgress}
          onClick={() => this.unblock(userTrack.id)}>ブロック解除</button>;
    } else {
      button = <button
          disabled={this.state.inProgress}
          onClick={() => this.block(userTrack.id)}>ブロック</button>;
    }

    return (
        <tr key={userTrack.id}
            style={{backgroundColor: userTrack.isBlocked() ? '#cccccc' : ''}}>
          <td>{this.props.rank}</td>
          <td>{userTrack.name}</td>
          <td>{userTrack.userArtists.map((a) => a.name).join(", ")}</td>
          <td>{button}</td>
        </tr>
    )
  }
}

interface ArtistRowProps {
  userArtist: UserArtist;
  updateParent: Function;
}


class ArtistRow extends React.Component<ArtistRowProps, CommonState> {
  constructor(props: ArtistRowProps) {
    super(props);
    this.state = {inProgress: false};
  }

  block(artistId: string) {
    if (this.state.inProgress) {
      return;
    }
    this.setState({inProgress: true})
    const url = `${BASE_URL}/artists/${artistId}/block`;
    fetch(url, {method: 'POST'}).then(() => {
      this.props.userArtist.blocked = true;
      this.setState({inProgress: false})
      this.props.updateParent();
    })
  }

  unblock(artistId: string) {
    if (this.state.inProgress) {
      return;
    }

    this.setState({inProgress: true})
    const url = `${BASE_URL}/artists/${artistId}/unblock`;
    fetch(url, {
      method: 'POST'
    }).then(() => {
      this.props.userArtist.blocked = false;
      this.setState({inProgress: false})
      this.props.updateParent();
    });
  }

  render() {
    const userArtist = this.props.userArtist;
    let button;
    if (!userArtist.blocked) {
      button = <button
          disabled={this.state.inProgress}
          onClick={() => this.block(userArtist.id)}>ブロック</button>;
    } else {
      button = <button
          disabled={this.state.inProgress}
          onClick={() => this.unblock(userArtist.id)}>ブロック解除</button>;
    }

    return <tr
        key={userArtist.id}
        style={{backgroundColor: userArtist.isBlocked() ? '#cccccc' : ''}}>
      <td>{userArtist.name}</td>
      <td>{button}</td>
    </tr>
  }
}

interface ReplacePlaylistButtonState {
  inProgress: boolean;
}

class ReplacePlaylistButton extends React.Component<any, ReplacePlaylistButtonState> {
  constructor(props: any) {
    super(props);
    this.state = {
      inProgress: false
    }
  }

  replacePlaylist = () => {
    if (this.state.inProgress) {
      return;
    }

    this.setState({inProgress: true});
    fetch(BASE_URL + '/replace_playlist', {
      method: 'POST'
    }).then((r) => {
    }).finally(() => this.setState({inProgress: false}))
  }

  render() {
    return <button
        onClick={() => this.replacePlaylist()}
        disabled={this.state.inProgress}>プレイリスト更新
    </button>
  }
}


interface TrackTableProps {
}

interface TrackTableState {
  userTracks: UserTrack[];
  userArtists: UserArtist[];
  inProgress: boolean;
}

export class TrackTable extends React.Component<TrackTableProps, TrackTableState> {
  constructor(props: TrackTableProps) {
    super(props);
    this.state = {
      userTracks: [],
      userArtists: [],
      inProgress: false,
    };
  }

  componentDidMount() {
    fetch(BASE_URL + '/tracks_and_artists')
    .then(res => res.json())
    .then((data) => {
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

