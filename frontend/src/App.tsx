import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AuthProvider } from "./context/AuthProvider"
import Layout from "./components/Layout/Layout"
import HomePage from "./pages/HomePage/HomePage"
import LoginPage from "./pages/LoginPage/LoginPage"
import RegisterPage from "./pages/RegisterPage/RegisterPage"
import CoursePage from "./pages/CoursePage/CoursePage"
import CourseEditPage from "./pages/CourseEditPage/CourseEditPage"
import UsersAdminPage from "./pages/UsersAdminPage/UsersAdminPage"
import CoursesPage from './pages/CoursesPage/CoursesPage'
import "./styles";

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Layout>
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                        <Route path="/courses/:id" element={<CoursePage />} />
                        <Route path="/courses/:id/edit" element={<CourseEditPage />} />
                        <Route path="/courses/create" element={<CourseEditPage />} />
                        <Route path="/admin/users" element={<UsersAdminPage />} />
                        <Route path="/courses" element={<CoursesPage />} />
                    </Routes>
                </Layout>
            </AuthProvider>
        </BrowserRouter>
    )
}

export default App