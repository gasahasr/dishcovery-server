import SwiftUI
import FirebaseAuth

class AuthViewModel: ObservableObject {
    @Published var user: User? = nil
    @Published var isSignedIn: Bool = false
    @Published var errorMessage: String = ""
    @Published var showError: Bool = false
    @Published var isLoading: Bool = false
    
    private var stateListener: AuthStateDidChangeListenerHandle?

    init() {
        self.user = Auth.auth().currentUser
        self.isSignedIn = user != nil
        
        // Listen for authentication state changes
        stateListener = Auth.auth().addStateDidChangeListener { [weak self] _, user in
            DispatchQueue.main.async {
                self?.user = user
                self?.isSignedIn = user != nil
            }
        }
    }
    
    deinit {
        // Remove the listener when the view model is deallocated
        if let listener = stateListener {
            Auth.auth().removeStateDidChangeListener(listener)
        }
    }

    func signUp(email: String, password: String) {
        guard !email.isEmpty, !password.isEmpty else {
            self.errorMessage = "Please fill in all fields"
            self.showError = true
            return
        }
        
        isLoading = true
        
        Auth.auth().createUser(withEmail: email, password: password) { [weak self] result, error in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                if let error = error {
                    self?.errorMessage = error.localizedDescription
                    self?.showError = true
                    return
                }
                
                self?.user = result?.user
                self?.isSignedIn = true
            }
        }
    }

    func signIn(email: String, password: String) {
        guard !email.isEmpty, !password.isEmpty else {
            self.errorMessage = "Please fill in all fields"
            self.showError = true
            return
        }
        
        isLoading = true
        
        Auth.auth().signIn(withEmail: email, password: password) { [weak self] result, error in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                if let error = error {
                    self?.errorMessage = error.localizedDescription
                    self?.showError = true
                    return
                }
                
                self?.user = result?.user
                self?.isSignedIn = true
            }
        }
    }

    func signOut() {
        isLoading = true
        
        do {
            try Auth.auth().signOut()
            self.user = nil
            self.isSignedIn = false
            self.isLoading = false
        } catch {
            self.errorMessage = error.localizedDescription
            self.showError = true
            self.isLoading = false
        }
    }
}
