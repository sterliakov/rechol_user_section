import { Calendar } from '@fullcalendar/core';
import interactionPlugin, { Draggable } from '@fullcalendar/interaction';
import enLocale from '@fullcalendar/core/locales/en-gb';
import deLocale from '@fullcalendar/core/locales/de';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';

global.Calendar = Calendar;
global.Draggable = Draggable;
global.interactionPlugin = interactionPlugin;
global.dayGridPlugin = dayGridPlugin;
global.timeGridPlugin = timeGridPlugin;
global.enLocale = enLocale;
global.deLocale = deLocale;
