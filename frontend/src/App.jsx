import { useEffect, useMemo, useState } from 'react'

const API = '/api/v1'
const roomCodes = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
const blankForm = { room_code: 'T1', booking_date: '', start_time: '08:00', end_time: '09:00', purpose: '' }

async function request(path, { token, ...options } = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options?.headers },
  })
  const data = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) throw new Error(data?.detail || `Request failed (${response.status})`)
  return data
}

function todayString() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(new Date())
}

export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem('ccc-token') || '')
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [login, setLogin] = useState({ username: '', password: '' })
  const [startDate, setStartDate] = useState(todayString)
  const [schedule, setSchedule] = useState([])
  const [requests, setRequests] = useState([])
  const [pending, setPending] = useState([])
  const [emailLogs, setEmailLogs] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [form, setForm] = useState({ ...blankForm, booking_date: todayString() })

  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => {
    const d = new Date(`${startDate}T12:00:00+05:30`)
    d.setDate(d.getDate() + i)
    return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(d)
  }), [startDate])

  async function loadAvailability() {
    try { setSchedule(await request(`/rooms/availability?from=${startDate}&days=7`)) }
    catch (e) { setError(e.message) }
  }

  async function loadUser() {
    if (!token) { setUser(null); return }
    try { setUser(await request('/auth/me', { token })) }
    catch { sessionStorage.removeItem('ccc-token'); setToken(''); setUser(null) }
  }

  async function loadRoleData(role = user?.role) {
    if (!token || !role) return
    try {
      if (role === 'FACULTY') setRequests(await request('/booking-requests/mine', { token }))
      if (role === 'ADMIN') {
        const [p, e, a] = await Promise.all([
          request('/admin/booking-requests?status=PENDING', { token }),
          request('/admin/email-logs', { token }), request('/admin/audit-logs', { token }),
        ])
        setPending(p); setEmailLogs(e); setAuditLogs(a)
      }
    } catch (e) { setError(e.message) }
  }

  useEffect(() => { loadAvailability() }, [startDate])
  useEffect(() => { loadUser() }, [token])
  useEffect(() => { if (user) loadRoleData(user.role) }, [user])

  async function doLogin(event) {
    event.preventDefault(); setError(''); setNotice('')
    try {
      const result = await request('/auth/login', { method: 'POST', body: JSON.stringify(login) })
      sessionStorage.setItem('ccc-token', result.access_token); setToken(result.access_token); setUser(result.user)
      setLogin({ username: '', password: '' }); setNotice(`Signed in as ${result.user.display_name}`)
    } catch (e) { setError(e.message) }
  }

  function logout() { sessionStorage.removeItem('ccc-token'); setToken(''); setUser(null); setNotice('Signed out') }

  async function submitBooking(event) {
    event.preventDefault(); setError(''); setNotice('')
    try {
      await request('/booking-requests', { token, method: 'POST', body: JSON.stringify(form) })
      setNotice('Request submitted for CCC administrator review.')
      setForm({ ...blankForm, booking_date: todayString() }); loadRoleData('FACULTY')
    } catch (e) { setError(e.message) }
  }

  async function decide(id, choice) {
    setError(''); setNotice('')
    try {
      await request(`/admin/booking-requests/${id}/${choice}`, { token, method: 'POST' })
      setNotice(`Request ${choice}d.`); loadRoleData('ADMIN'); loadAvailability()
    } catch (e) { setError(e.message) }
  }

  async function cancelBooking(id) {
    if (!window.confirm('Cancel this confirmed booking?')) return
    try { await request(`/admin/bookings/${id}/cancel`, { token, method: 'POST' }); setNotice('Booking cancelled.'); loadAvailability() }
    catch (e) { setError(e.message) }
  }

  const byRoomDate = new Map(schedule.map((entry) => [`${entry.room_code}-${entry.date}`, entry]))

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-5 py-4 lg:px-8">
          <div><p className="text-xs font-semibold uppercase tracking-[.17em] text-teal-700">National Institute of Technology Calicut</p><h1 className="mt-1 text-xl font-semibold">CCC Terminal Booking Tracker</h1></div>
          <div className="flex items-center gap-3">{user ? <><span className="text-sm text-slate-600">{user.display_name} · {user.role}</span><button className="button-secondary" onClick={logout}>Sign out</button></> : <span className="text-sm text-slate-500">Availability · IST</span>}</div>
        </div>
      </header>
      <div className="mx-auto max-w-7xl space-y-7 px-5 py-8 lg:px-8">
        {(error || notice) && <div role="status" className={`rounded-lg px-4 py-3 text-sm ${error ? 'bg-rose-50 text-rose-800' : 'bg-teal-50 text-teal-900'}`}>{error || notice}<button className="float-right font-semibold" onClick={() => { setError(''); setNotice('') }}>×</button></div>}

        <section className="rounded-2xl bg-slate-900 px-6 py-7 text-white sm:px-8">
          <div className="flex flex-wrap items-end justify-between gap-5"><div><p className="text-sm font-medium text-teal-300">Central Computer Centre</p><h2 className="mt-2 text-3xl font-semibold tracking-tight">Terminal room availability</h2><p className="mt-2 max-w-xl text-sm leading-6 text-slate-300">View confirmed bookings across all six rooms. All times are Indian Standard Time.</p></div>
            <label className="text-sm text-slate-300">Week starting <input className="ml-2 rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-white" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} /></label>
          </div>
        </section>

        <section className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="min-w-[1000px]">
            <div className="grid grid-cols-[100px_repeat(7,minmax(120px,1fr))] border-b bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500"><div className="p-3">Room</div>{days.map((day) => <div key={day} className="border-l p-3">{new Intl.DateTimeFormat('en-IN', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'Asia/Kolkata' }).format(new Date(`${day}T12:00:00+05:30`))}</div>)}</div>
            {roomCodes.map((room) => <div key={room} className="grid grid-cols-[100px_repeat(7,minmax(120px,1fr))] border-b last:border-0"><div className="p-3 font-semibold">{room}</div>{days.map((day) => { const data = byRoomDate.get(`${room}-${day}`); const busy = new Set((data?.slots || []).filter((s) => s.status === 'BOOKED').map((s) => s.start)); return <div key={day} className="border-l p-2"><div className="grid grid-cols-3 gap-1">{Array.from({ length: 12 }, (_, i) => { const time = `${String(i + 8).padStart(2, '0')}:00`; return <span title={`${time} IST · ${busy.has(time) ? 'Booked' : 'Available'}`} key={time} className={`rounded px-1 py-1 text-center text-[10px] font-medium ${busy.has(time) ? 'bg-rose-100 text-rose-800' : 'bg-teal-50 text-teal-800'}`}>{time.slice(0, 2)}</span> })}</div></div> })}</div>)}
          </div>
          <div className="flex gap-4 border-t px-4 py-3 text-xs text-slate-600"><span><i className="mr-1 inline-block h-2.5 w-2.5 rounded-sm bg-teal-200" />Available</span><span><i className="mr-1 inline-block h-2.5 w-2.5 rounded-sm bg-rose-200" />Confirmed booking</span></div>
        </section>

        {!user && <section className="grid gap-6 md:grid-cols-[1fr_360px]"><div className="rounded-xl border border-slate-200 bg-white p-6"><h3 className="text-lg font-semibold">Need to submit a request?</h3><p className="mt-2 text-sm leading-6 text-slate-600">Faculty can sign in with their application account to request a room. Student accounts are view-only.</p></div><form onSubmit={doLogin} className="space-y-3 rounded-xl border border-slate-200 bg-white p-6"><h3 className="font-semibold">Application sign in</h3><input className="input" autoComplete="username" placeholder="Username" value={login.username} onChange={(e) => setLogin({ ...login, username: e.target.value })} required /><input className="input" type="password" autoComplete="current-password" placeholder="Password" value={login.password} onChange={(e) => setLogin({ ...login, password: e.target.value })} required /><button className="button-primary w-full">Sign in</button></form></section>}

        {user?.role === 'FACULTY' && <section className="grid gap-6 lg:grid-cols-[360px_1fr]"><form onSubmit={submitBooking} className="space-y-3 rounded-xl border border-slate-200 bg-white p-6"><h3 className="text-lg font-semibold">Request a terminal</h3><label className="field-label">Room<select className="input" value={form.room_code} onChange={(e) => setForm({ ...form, room_code: e.target.value })}>{roomCodes.map((r) => <option key={r}>{r}</option>)}</select></label><label className="field-label">Date<input className="input" type="date" min={todayString()} value={form.booking_date} onChange={(e) => setForm({ ...form, booking_date: e.target.value })} required /></label><div className="grid grid-cols-2 gap-3"><label className="field-label">Start (IST)<select className="input" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value, end_time: `${String(Number(e.target.value.slice(0, 2)) + 1).padStart(2, '0')}:00` })}>{Array.from({ length: 12 }, (_, i) => `${String(i + 8).padStart(2, '0')}:00`).map((t) => <option key={t}>{t}</option>)}</select></label><label className="field-label">End (IST)<select className="input" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })}>{Array.from({ length: 12 }, (_, i) => `${String(i + 9).padStart(2, '0')}:00`).map((t) => <option key={t}>{t}</option>)}</select></label></div><label className="field-label">Purpose<textarea className="input min-h-24" maxLength={500} value={form.purpose} onChange={(e) => setForm({ ...form, purpose: e.target.value })} required /></label><button className="button-primary w-full">Send for approval</button></form><div className="rounded-xl border border-slate-200 bg-white p-6"><h3 className="text-lg font-semibold">My booking requests</h3><div className="mt-4 divide-y">{requests.length ? requests.map((r) => <div key={r.id} className="flex flex-wrap justify-between gap-2 py-3 text-sm"><span><b>{r.room_code}</b> · {r.booking_date} · {r.start_time}–{r.end_time}<span className="block text-slate-500">{r.purpose}</span></span><span className="badge">{r.status}</span></div>) : <p className="py-5 text-sm text-slate-500">No requests yet.</p>}</div></div></section>}

        {user?.role === 'ADMIN' && <section className="space-y-6"><div className="rounded-xl border border-slate-200 bg-white p-6"><div className="flex items-center justify-between"><h3 className="text-lg font-semibold">Pending faculty requests</h3><button className="button-secondary" onClick={() => loadRoleData('ADMIN')}>Refresh</button></div><div className="mt-4 divide-y">{pending.length ? pending.map((r) => <div key={r.id} className="flex flex-wrap items-center justify-between gap-4 py-4"><div className="text-sm"><b>{r.room_code}</b> · {r.booking_date} · {r.start_time}–{r.end_time}<p className="mt-1 text-slate-600">{r.purpose}</p><p className="text-xs text-slate-400">Faculty account: {r.faculty_user_id}</p></div><div className="flex gap-2"><button className="button-primary" onClick={() => decide(r.id, 'approve')}>Approve</button><button className="button-secondary" onClick={() => decide(r.id, 'reject')}>Reject</button></div></div>) : <p className="py-5 text-sm text-slate-500">No pending requests.</p>}</div></div>
          <div className="grid gap-6 xl:grid-cols-2"><div className="rounded-xl border border-slate-200 bg-white p-6"><h3 className="text-lg font-semibold">Email processing</h3><div className="mt-4 space-y-3">{emailLogs.length ? emailLogs.map((e) => <article key={e.id} className="rounded-lg bg-slate-50 p-3 text-sm"><div className="flex justify-between gap-3"><b className="truncate">{e.subject || '(no subject)'}</b><span className="badge">{e.status}</span></div><p className="mt-1 truncate text-xs text-slate-500">{e.sender} {e.received_at ? `· ${new Date(e.received_at).toLocaleString()}` : ''}</p>{e.error && <p className="mt-2 text-xs text-rose-700">{e.error}</p>}</article>) : <p className="text-sm text-slate-500">No messages processed yet.</p>}</div></div><div className="rounded-xl border border-slate-200 bg-white p-6"><h3 className="text-lg font-semibold">Recent audit events</h3><div className="mt-4 space-y-2">{auditLogs.slice(0, 30).map((a) => <div key={a.id} className="flex justify-between gap-3 border-b py-2 text-xs"><span>{a.action} · {a.entity_type}</span><time className="shrink-0 text-slate-500">{new Date(a.created_at).toLocaleString()}</time></div>)}{!auditLogs.length && <p className="text-sm text-slate-500">No events recorded.</p>}</div></div></div>
          <div className="rounded-xl border border-slate-200 bg-white p-6"><h3 className="text-lg font-semibold">Confirmed bookings this week</h3><div className="mt-4 grid gap-2 md:grid-cols-2 xl:grid-cols-3">{schedule.flatMap((d) => (d.bookings || []).map((b) => ({ ...b, room: d.room_code, date: d.date }))).map((b) => <div key={b.id} className="flex items-center justify-between gap-2 rounded-lg bg-slate-50 p-3 text-sm"><span><b>{b.room}</b> · {b.date}<small className="block text-slate-600">{b.start}–{b.end} IST</small></span><button className="text-xs font-semibold text-rose-700" onClick={() => cancelBooking(b.id)}>Cancel</button></div>)}</div></div>
        </section>}
      </div>
      <footer className="border-t border-slate-200 px-5 py-5 text-center text-xs text-slate-500">NITC Central Computer Centre · Operating hours 08:00–20:00 IST</footer>
    </main>
  )
}
