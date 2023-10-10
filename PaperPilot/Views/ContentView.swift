//
//  ContentView.swift
//  PaperPilot
//
//  Created by 林思行 on 2023/9/24.
//

import SwiftUI
import SwiftData

struct ContentView: View {
    @Environment(\.modelContext) private var modelContext
    
    @Query private var projects: [Project]
    @State private var selectedProject: Project?
    @State private var isShowingLoginSheet = false
    @State private var isShowingAccountView = false
    @State private var isShowingNewProjectSheet = false
    
    @AppStorage(AppStorageKey.User.loggedIn.rawValue)
    private var loggedIn = false
    
    var body: some View {
        NavigationSplitView {
            // MARK: - 项目列表
            List(selection: $selectedProject) {
                Section("Local Projects") {
                    ForEach(projects) { project in
                        NavigationLink(project.name, value: project)
                    }
                    .contextMenu {
                        Button("Delete") {
                            modelContext.delete(selectedProject!)
                            selectedProject = nil
                        }
                    }
                }
            }
            .navigationTitle("Projects")
            .frame(minWidth: 180)
            .toolbar {
                ToolbarItem {
                    Button("New Project", systemImage: "folder.badge.plus") {
                        isShowingNewProjectSheet.toggle()
                    }
                    .sheet(isPresented: $isShowingNewProjectSheet) {
                        ProjectCreateEditView()
                    }
                }
            }
        } detail: {
            // MARK: - 项目详情
            Group {
                if let project = selectedProject {
                    ProjectDetail(project: project)
                } else {
                    Text("Select a project from the left sidebar.")
                        .font(.title)
                        .foregroundStyle(.secondary)
                }
            }
        }
        // MARK: - Toolbar
        .toolbar {
            ToolbarItem {
                if !loggedIn {
                    Button {
                        isShowingLoginSheet.toggle()
                    } label: {
                        HStack {
                            Image(systemName: "person.crop.circle")
                            Text("Login")
                        }
                    }
                    .sheet(isPresented: $isShowingLoginSheet) {
                        LoginSheet()
                    }
                } else {
                    Button("Account", systemImage: "person.crop.circle") {
                        isShowingAccountView.toggle()
                    }
                    
                    .sheet(isPresented: $isShowingAccountView) {
                        AccountView()
                    }
                }
            }
        }
    }
}

#Preview {
    ContentView()
        .modelContainer(previewContainer)
}
