# System Architecture - Standalone Raspberry Pi Project

> Status: core, plugin system, navigator and tests are implemented.
> Input devices, the renderer and the display backend are planned.

## 1. Component Diagram

```mermaid
graph TD
    subgraph Hardware [Physical Hardware]
        Display[3.5 DSI Display]
        Strip[10-Sensor Strip / 5 Zones]
        Keyboard[Keyboard - development]
    end

    subgraph HAL [hal - Hardware Abstraction Layer]
        InputDevice[Input devices - own thread]
        HalDisplay[Display backend]
    end

    subgraph Core [core]
        EventBus[EventBus - queue + publish]
        StateMgr[StateManager]
        PluginMgr[PluginManager - discovers *_plugin.py]
        Context[AppContext]
    end

    subgraph UI [ui]
        Navigator[Navigator - screens and actions]
        Renderer[Renderer]
    end

    subgraph Plugins [plugins]
        Menu[menu]
        Wifi[wifi]
        AiAgent[ai_agent]
    end

    Main[main.py - builds and wires everything]

    Keyboard --> InputDevice
    Strip --> InputDevice
    InputDevice -->|post InputEvent| EventBus
    Main --> Context
    Context --- EventBus
    Context --- StateMgr
    Context --- Navigator
    PluginMgr -->|start ctx| Plugins
    Plugins -->|post / set| EventBus
    Plugins --> StateMgr
    Plugins --> Navigator
    EventBus -->|notify| Renderer
    Renderer --> HalDisplay
    HalDisplay --> Display
```

## 2. Input Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Device as Input device (own thread)
    participant Bus as EventBus
    participant Main as main loop
    participant Menu as MenuPlugin
    participant Nav as Navigator
    participant Render as Renderer
    participant Disp as Display

    User->>Device: key / touch zone
    Device->>Bus: post(INPUT_ACTION, InputEvent)
    Note over Bus: queued, thread-safe
    Main->>Bus: dispatch_next_event()
    Bus->>Menu: publish(INPUT_ACTION)
    Menu->>Nav: get_active_screen()
    Menu->>Menu: move selection
    Menu->>Bus: post(UI_UPDATE)
    Main->>Bus: dispatch_next_event()
    Bus->>Render: publish(UI_UPDATE)
    Render->>Disp: draw screen
    Disp->>User: refreshed display
```

## 3. Rules

- **Threads**: only input devices run in their own thread. They use
  `EventBus.post()` and nothing else. All subscribers run in the main
  thread, one event at a time.
- **post vs publish**: `post` queues an event (any thread). `publish`
  delivers immediately and is called by the main thread only
  (inside `dispatch_next_event`, or by `StateManager`).
- **Dependencies point one way**: `plugins` -> `ui`, `core`;
  `ui` and `hal` -> `core`; `core` imports nothing from the others
  at runtime (type-only imports go under `TYPE_CHECKING`).
- **Plugins** live in `plugins/<name>/<name>_plugin.py`, extend `Plugin`
  and talk to the rest only through `ctx` (events and state), never by
  importing each other.
- **Wiring**: `main.py` is the only place that creates the services and
  passes them down.