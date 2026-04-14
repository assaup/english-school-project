import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./context/AuthProvider"
import { useAuth } from "./context/useAuth"
import { LoginPage } from "./pages/LoginPage/LoginPage"
import { CoursesPage } from "./pages/CoursesPage/CoursesPage"
import { CourseDetailPage } from "./pages/CourseDetailPage/CourseDetailPage"
import { DashboardPage } from "./pages/DashboardPage/DashboardPage"
import { Header } from "./components/Header/Header"
import "./styles/global.scss"

function PrivateRoute({ children }: { children: React.ReactNode }) {
    const { user, loading } = useAuth()

    if (loading) {
        return <div>Загрузка...</div>
    }

    return user ? <>{children}</> : <Navigate to="/login" />
}

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route
                        path="/dashboard"
                        element={
                            <>
                                <Header />
                                <PrivateRoute>
                                    <DashboardPage />
                                </PrivateRoute>
                            </>
                        }
                    />
                    <Route
                        path="/courses"
                        element={
                            <>
                                <Header />
                                <PrivateRoute>
                                    <CoursesPage />
                                </PrivateRoute>
                            </>
                        }
                    />
                    <Route
                        path="/courses/:id"
                        element={
                            <>
                                <Header />
                                <PrivateRoute>
                                    <CourseDetailPage />
                                </PrivateRoute>
                            </>
                        }
                    />
                    <Route path="/" element={<Navigate to="/dashboard" />} />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    )
}

export default App
